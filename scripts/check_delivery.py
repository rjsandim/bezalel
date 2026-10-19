#!/usr/bin/env python3
"""Confere declarações de entrega, sem executar ferramentas ou autenticar decisões."""
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlparse
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DIMENSIONS = {"files", "database", "queues", "ports", "storage"}
STAGES = ("plan", "database", "investigate", "implement", "accept", "deliver", "handoff", "accepted", "merged", "finish", "close")
DEVELOPERS = {"dev-fullstack", "backend", "frontend-web", "mobile"}


class ContractError(ValueError):
    """Diagnóstico fixo, sem reproduzir dados privados da entrada."""


def require(condition, message):
    if not condition:
        raise ContractError(message)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def local_file(project, value, label):
    require(text(value) and not Path(value).is_absolute(), label + ": informe caminho relativo ao projeto.")
    try:
        target = (project / value).resolve()
    except (OSError, ValueError, RuntimeError):
        raise ContractError(label + ": caminho local inválido.") from None
    require(project in target.parents and target.is_file(), label + ": arquivo ausente ou fora do projeto.")
    return target


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError):
        raise ContractError("Não foi possível ler JSON válido; conteúdo omitido.") from None


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()


def file_digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def timestamp(value):
    try:
        when = datetime.fromisoformat(value.replace("Z", "+00:00"))
        require(when.tzinfo is not None, "Data precisa incluir fuso.")
        return when
    except (TypeError, AttributeError, ValueError):
        raise ContractError("Data com fuso inválida.") from None


def https_reference(value):
    if not text(value):
        return False
    try:
        parsed = urlparse(value)
        return parsed.scheme == "https" and bool(parsed.hostname) and not parsed.username and not parsed.password and bool(parsed.path.strip("/"))
    except ValueError:
        return False


def validate_config(config, project=None):
    fields = {"schema_version", "project", "context", "interfaces", "checks", "production_branches"}
    require(isinstance(config, dict) and set(config) == fields, "Configuração do projeto: campos ausentes/desconhecidos; não declare permissões, credenciais ou observadores.")
    require(type(config["schema_version"]) is int and config["schema_version"] == 2 and text(config["project"]), "Use schema_version 2 e nome do projeto; migre o formato 1 explicitamente.")
    context = config["context"]
    require(isinstance(context, dict) and set(context) == {"architecture", "business"}, "Declare contexto de arquitetura e negócio.")
    for value in context.values():
        require(text(value), "Referência de contexto vazia.")
        if project is not None:
            local_file(project, value, "Contexto")
    require(isinstance(config["interfaces"], list) and all(isinstance(item, str) and item in {"api", "web", "mobile"} for item in config["interfaces"]), "Interfaces inválidas.")
    checks = config["checks"]
    require(isinstance(checks, dict) and set(checks) == {"test", "lint", "build"}, "Declare test/lint/build.")
    require(all(isinstance(command, list) and all(text(arg) for arg in command) for command in checks.values()), "Comandos são listas de argumentos; não são executados pelo validador.")
    branches = config["production_branches"]
    require(isinstance(branches, dict) and branches and all(text(repo) and text(branch) for repo, branch in branches.items()), "Declare branch de produção real por repositório, sem presumir main/master.")


def human_decision(value, subject, decision="approved"):
    require(isinstance(value, dict) and value.get("decision") == decision, "Decisão humana aplicável ausente.")
    require(value.get("actor_type") == "human" and all(text(value.get(k)) for k in ("actor", "source")), "Identifique pessoa e fonte da decisão humana real.")
    timestamp(value.get("recorded_at"))
    require(value.get("subject") == subject, "Objeto difere da versão aprovada; reconfira decisão humana.")


def passed(value, label, candidate=None):
    require(isinstance(value, dict) and value.get("status") == "passed" and text(value.get("evidence")), label + ": resultado passado com evidência ausente.")
    if candidate is not None:
        require(value.get("candidate") == candidate, label + ": evidência de outro candidato.")


def independent(value, implementers, label):
    require(isinstance(value, dict) and text(value.get("reviewer")) and value["reviewer"].strip() not in {actor.strip() for actor in implementers}, label + ": revisor precisa ser distinto dos implementadores.")


def verify_isolation(isolation):
    require(isinstance(isolation, dict) and set(isolation) == DIMENSIONS, "Isolamento deve cobrir arquivos, banco, filas, portas e storage.")
    for dimension, result in isolation.items():
        require(isinstance(result, dict), "Registro de isolamento inválido.")
        if result.get("status") == "verified":
            require(text(result.get("evidence")), "Isolamento verificado exige evidência.")
        else:
            require(dimension != "files" and result.get("status") == "not_applicable" and text(result.get("reason")), "Isolamento pendente ou não aplicável sem justificativa.")


def scope_subject(issue):
    return "scope:" + digest({k: v for k, v in issue.items() if k != "approval"})


def issue_criteria(issue, scenario):
    require(text(issue.get("scope_ref")) and text(issue.get("dependencies")), "Escopo/referência e dependências são obrigatórios para execução.")
    groups = [issue.get("criteria")]
    stories = issue.get("stories", [])
    require(isinstance(stories, list), "Histórias inválidas.")
    if scenario == "feature":
        require(stories and all(isinstance(s, dict) and (s.get("url") is None or https_reference(s.get("url")))
                and text(s.get("scope_ref")) for s in stories), "Feature exige histórias vinculadas com escopo identificado.")
        references = {s.get('url') or s['scope_ref'] for s in stories}
        require(len(references) == len(stories) and (issue.get('url') or issue['scope_ref']) not in references,
                "Histórias precisam de referências distintas da principal.")
        groups.extend(s.get("criteria") for s in stories)
    else:
        require(not stories, "Histórias de conjunto pertencem ao cenário feature.")
    ids = []
    for group in groups:
        require(isinstance(group, list) and group and all(isinstance(c, dict) and text(c.get("id")) and text(c.get("text")) for c in group), "Declare critérios observáveis com ID e texto.")
        ids.extend(c["id"] for c in group)
    require(len(set(ids)) == len(ids), "Critérios duplicados; use IDs únicos entre histórias e conjunto.")
    return set(ids)


def proposal_subject(database):
    return "proposal:" + digest({k: database.get(k) for k in (
        "proposal_sha256", "base_ref", "scope", "schema_change", "migration", "complex_relations")})


def proposal_path(project, value):
    require(text(value), "Informe o HTML temporário da proposta.")
    relative = Path(value)
    require(not relative.is_absolute() and '..' not in relative.parts
            and relative.parts[:2] == ('.bezalel', 'reviews') and relative.suffix == '.html',
            "Proposta deve ser HTML temporário em .bezalel/reviews/.")
    path = project
    for part in relative.parts:
        path = path / part
        require(not path.is_symlink(), "Proposta não pode usar symlinks.")
    return path


def verify_database(database, project, scope, reviewing=False):
    require(isinstance(database, dict), "Declare impacto de banco.")
    impacts = ("schema_change", "migration", "complex_relations")
    require(all(type(database.get(k)) is bool for k in impacts), "Classifique estrutura, qualquer migration e relações complexas.")
    require(text(database.get("reason")), "Classificação de banco exige justificativa.")
    if not any(database[k] for k in impacts):
        require(not database.get("approval") and not database.get("proposal"), "Não invente aprovação de banco não aplicável.")
        return
    proposal = proposal_path(project, database.get("proposal"))
    require(text(database.get("proposal_sha256")) and re.fullmatch('[a-f0-9]{64}', database["proposal_sha256"]) is not None
            and text(database.get("base_ref")) and database.get("scope") == scope,
            "Identifique hash do HTML, base real e escopo atual da proposta.")
    require(text(database.get("proposal_ref")) and text(database.get("summary")),
            "Preserve referência e resumo da proposta na issue, PR ou conversa.")
    subject = proposal_subject(database)
    if database["complex_relations"]:
        review = database.get("review")
        passed(review, "Revisão técnica de banco")
        require(text(review.get("reviewer")) and review.get("subject") == subject,
                "Relação complexa exige revisor identificado e parecer da proposta exata.")
    if reviewing:
        require(proposal.is_file() and proposal.stat().st_size > 0, "HTML da proposta ausente ou vazio.")
        require(file_digest(proposal) == database["proposal_sha256"], "HTML mudou; revise hash e decisão.")
        html = proposal.read_text(encoding="utf-8").lower()
        require('<!doctype html>' in html and '<html' in html and '</html>' in html,
                "Proposta deve ser um documento HTML; conteúdo precisa de revisão humana.")
        return
    human_decision(database.get("approval"), subject)
    cleanup = database.get("cleanup")
    require(isinstance(cleanup, dict) and cleanup.get("status") == "deleted"
            and text(cleanup.get("evidence")) and not proposal.exists(),
            "Após registrar a decisão final, exclua o HTML temporário e registre a confirmação.")
    require(timestamp(cleanup.get("deleted_at")) >= timestamp(database['approval']['recorded_at']),
            "Remoção do HTML deve ocorrer depois da decisão registrada.")


def candidate_subject(candidate, config):
    require(isinstance(candidate, dict) and set(candidate) == {"id", "repositories", "context_ref"} and text(candidate["id"]) and text(candidate["context_ref"]), "Identifique candidato e contexto de componentes/builds, schema, dados e configuração.")
    repos = candidate["repositories"]
    require(isinstance(repos, list) and repos and all(isinstance(r, dict) and set(r) == {"name", "base", "head"} and all(text(v) for v in r.values()) for r in repos), "Declare todos os repositórios com base/head.")
    require(len({r["name"] for r in repos}) == len(repos), "Repositório duplicado no candidato.")
    for repo in repos:
        require(config["production_branches"].get(repo["name"]) == repo["base"], "Base do candidato difere da produção configurada.")
    return "candidate:" + digest(candidate)


def verify_security(security, implementers, candidate):
    independent(security, implementers, "AppSec")
    passed(security, "AppSec", candidate)
    require(text(security.get("coverage")) and security.get("material_gap") is False, "Cobertura/lacuna material de segurança impede conclusão.")
    findings = security.get("findings")
    require(isinstance(findings, list), "Informe achados de AppSec, inclusive lista vazia quando realmente verificada.")
    ids = []
    for finding in findings:
        require(isinstance(finding, dict) and all(text(finding.get(k)) for k in ("id", "summary", "evidence")) and finding.get("severity") in {"critical", "high", "medium", "low"} and finding.get("confidence") in {"high", "medium", "low"}, "Achado precisa de identidade, descrição, severidade/confiança e evidência.")
        ids.append(finding["id"])
        disposition = finding.get("disposition")
        require(disposition in {"fixed", "false_positive", "deferred"}, "Hipótese ou achado sem tratamento bloqueia; investigue ou registre interrupção.")
        require(finding.get("classification") == ("false_positive" if disposition == "false_positive" else "confirmed"), "Diferencie hipótese, confirmação e falso positivo antes de concluir.")
        if disposition == "deferred":
            require(finding["severity"] in {"medium", "low"}, "Crítico/alto não pode ser adiado.")
            require(all(text(finding.get(k)) for k in ("reason", "owner", "deadline_or_condition")), "Adiamento exige motivo, dono e prazo/condição.")
            subject = "risk:" + digest({"candidate": candidate, "finding": {k: v for k, v in finding.items() if k != "approval"}})
            human_decision(finding.get("approval"), subject)
    require(len(ids) == len(set(ids)), "Achado de segurança duplicado.")


def verify_qa(qa, implementers, candidate, criteria, scenario):
    independent(qa, implementers, "QA")
    passed(qa, "QA", candidate)
    results = qa.get("criteria")
    require(isinstance(results, list) and all(isinstance(r, dict) and text(r.get("id")) for r in results), "Resultados de QA inválidos.")
    require(len(results) == len(criteria) and {r["id"] for r in results} == criteria, "QA deve cobrir todos os critérios de histórias e conjunto, uma vez cada.")
    for result in results:
        passed(result, "Critério", candidate)
    for key in (["additional_scenarios", "journeys"] if scenario == "feature" else ["additional_scenarios"]):
        scenarios = qa.get(key)
        require(isinstance(scenarios, list) and scenarios, "QA exige cenário adicional; feature também exige jornada global.")
        for item in scenarios:
            require(isinstance(item, dict) and all(text(item.get(k)) for k in ("name", "basis", "expected")), "Cenário/jornada precisa de origem e resultado esperado.")
            passed(item, "Cenário/jornada", candidate)


def verify_accept_package(record, project, config, criteria):
    candidate = candidate_subject(record.get("candidate"), config)
    implementers = record["implementers"]
    integration = record.get("integration")
    passed(integration, "Integração", candidate)
    require(integration.get("owner") == record["owner"], "O dev responsável precisa assumir a integração inteira.")
    review = record.get("review")
    independent(review, implementers, "TL")
    passed(review, "Revisão TL", candidate)
    checks = record.get("checks")
    require(isinstance(checks, list) and checks, "Declare verificações por impacto e obrigatoriedade.")
    for check in checks:
        require(isinstance(check, dict) and text(check.get("name")) and type(check.get("required")) is bool, "Verificação precisa de nome e obrigatoriedade.")
        if check.get("status") == "not_applicable":
            require(check["required"] is False and text(check.get("reason")), "Verificação obrigatória não pode ser dispensada.")
        else:
            passed(check, "Verificação", candidate)
    verify_security(record.get("security"), implementers, candidate)
    verify_qa(record.get("qa"), implementers, candidate, criteria, record["scenario"])
    manual = record.get("manual_test")
    require(isinstance(manual, dict) and manual.get("candidate") == candidate, "Roteiro precisa do mesmo candidato.")
    path = local_file(project, manual.get("path"), "Roteiro")
    require(path.stat().st_size > 0, "Roteiro vazio.")
    if record["scenario"] in {"improvement", "feature"}:
        require(path.suffix.lower() == ".xlsx" and zipfile.is_zipfile(path), "Melhoria/feature exigem roteiro Excel válido; conteúdo requer conferência humana.")
    return candidate, "accept:" + digest({"candidate": candidate, "manual_sha256": file_digest(path)})


def delivery_prs(record):
    prs = record.get("pull_requests")
    repos = record["candidate"]["repositories"]
    require(isinstance(prs, list) and len(prs) == len(repos) and all(isinstance(p, dict) and text(p.get("repository")) for p in prs), "Verifique todas as PRs necessárias.")
    require({p["repository"] for p in prs} == {r["name"] for r in repos}, "PRs ausentes ou duplicadas.")
    require(all(https_reference(p.get("url")) for p in prs) and len({p["url"] for p in prs}) == len(prs), "PRs precisam de URLs distintas e válidas.")
    return prs


def verify_handoff(record, config, candidate):
    prs = delivery_prs(record)
    repos = record["candidate"]["repositories"]
    for pr in prs:
        repo = next(r for r in repos if r["name"] == pr["repository"])
        require(https_reference(pr.get("url")) and pr.get("base") == repo["base"] and pr.get("head") == repo["head"] and pr.get("state") == "open", "PR precisa estar aberta/verificada na base/head validados.")
        timestamp(pr.get("verified_at"))
        ci = pr.get("ci")
        require(isinstance(ci, dict) and ci.get("status") in {"passed", "pending", "failed", "not_applicable"} and text(ci.get("evidence")), "Informe CI pós-abertura no estado observado.")
    handoff = record.get("handoff")
    passed(handoff, "Handoff", candidate)
    require(text(handoff.get("next_steps")), "Entregue próximos passos manuais, inclusive CI pendente/falho.")


def environment_subject(environment):
    return "environment:" + digest(environment)


def verify_completion(record, config, finish=False):
    """Confere registros; nunca consulta GitHub, fecha issue ou remove recursos."""
    candidate = candidate_subject(record.get("candidate"), config)
    completion = record.get("completion")
    require(isinstance(completion, dict), "Registre a conferência após aprovação ou aviso de merge.")
    trigger = completion.get("trigger")
    require(isinstance(trigger, dict) and trigger.get("kind") in {"approved", "merge_reported"}
            and trigger.get("actor_type") == "human" and trigger.get("candidate") == candidate
            and all(text(trigger.get(k)) for k in ('actor', 'source')),
            "Retomada exige interação humana real vinculada à entrega; não infira merge da aprovação.")
    requested_at = timestamp(trigger.get("recorded_at"))
    verified_times = []
    for pr in delivery_prs(record):
        repo = next(r for r in record['candidate']['repositories'] if r['name'] == pr['repository'])
        require(pr.get('state') == 'merged' and pr.get('base') == repo['base'] and pr.get('head') == repo['head']
                and text(pr.get('merge_commit')) and text(pr.get('evidence')),
                "Todas as PRs precisam de merge verificado da base/head da entrega; fechada não é mergeada.")
        verified = timestamp(pr.get('verified_at'))
        require(verified >= requested_at and verified >= timestamp(pr.get('merged_at')),
                "Confira o merge no serviço depois da mensagem humana; não reutilize consulta antiga.")
        verified_times.append(verified)
    if not finish:
        return
    require(completion.get('scope_complete') is True and text(completion.get('scope_evidence')),
            "Confirme o escopo completo; não encerre pendências ou histórias ainda abertas por inferência.")
    tracked = [record['issue'], *record['issue'].get('stories', [])]
    require(all(isinstance(i, dict) and (i.get('url') is None or https_reference(i.get('url'))) for i in tracked),
            "Referências de issues inválidas no encerramento.")
    expected_issues = {i['url'] for i in tracked if i.get('url')}
    issues = completion.get('issues')
    require(isinstance(issues, list) and all(isinstance(i, dict) for i in issues)
            and len(issues) == len(expected_issues) and {i.get('url') for i in issues} == expected_issues,
            "Confira as issues existentes do escopo; sem issue, registre lista vazia.")
    for issue in issues:
        require(issue.get('state') == 'closed' and text(issue.get('evidence'))
                and timestamp(issue.get('verified_at')) >= max(verified_times),
                "Issue deve estar fechada/verificada após conferir todos os merges.")
    environment, result = record.get('environment'), completion.get('environment')
    require(isinstance(environment, dict) and isinstance(result, dict), "Identifique ambiente e resultado de encerramento.")
    if environment.get('status') == 'not_applicable':
        require(text(environment.get('reason')) and text(environment.get('evidence'))
                and result.get('status') == 'not_applicable' and text(result.get('evidence')),
                "Ausência de ambiente gerenciado exige verificação; não crie ou adivinhe um alvo.")
        return
    require(all(text(environment.get(k)) for k in ('project', 'repository', 'branch', 'worktree', 'name', 'docker_context', 'ownership_evidence')),
            "Identifique projeto, repositório, branch da tarefa, worktree, ambiente e contexto Docker.")
    repos = {r['name']: r for r in record['candidate']['repositories']}
    require(environment['repository'] in repos and environment['branch'] != repos[environment['repository']]['base']
            and re.fullmatch('[a-z0-9][a-z0-9-]*', environment['name']) is not None,
            "Use o ambiente associado à branch da tarefa, nunca a base de produção ou um nome deduzido.")
    require(result.get('target') == environment_subject(environment) and result.get('status') == 'destroyed'
            and result.get('worktree_removed') is True
            and all(text(result.get(k)) for k in ('preservation_evidence', 'command_evidence', 'evidence')),
            "Encerramento exige preservação e destroy verificados do alvo exato; remoção parcial permanece pendente.")
    required_times = verified_times + [timestamp(i['verified_at']) for i in issues]
    require(timestamp(result.get('verified_at')) >= max(required_times), "Confira a limpeza depois de merges e issues.")


def disposition_subject(record):
    disposition = record["disposition"]
    return "disposition:" + digest({"issue": record["issue"].get("url") or record["issue"].get("scope_ref"), **{k: disposition.get(k) for k in ("kind", "reason", "target", "owner", "resume_condition")}})


def verify_disposition(record):
    disposition = record.get("disposition")
    require(isinstance(disposition, dict) and disposition.get("kind") in {"deferred", "discarded", "expected_behavior", "transferred"}, "Destino sem implementação inválido.")
    require(disposition["kind"] != "expected_behavior" or record["scenario"] == "bug", "Comportamento esperado é destino próprio do cenário bug.")
    human_decision(disposition.get("approval"), disposition_subject(record))
    require(text(disposition.get("reason")) and text(disposition.get("evidence")), "Registre motivo e verifique o estado real da issue.")
    if record['issue'].get('url') is None:
        require(disposition.get('issue_state') == 'not_applicable', "Sem issue, registre estado não aplicável; não invente fechamento remoto.")
    elif disposition["kind"] in {"discarded", "expected_behavior"}:
        require(disposition.get("issue_state") == "closed", "Encerramento exige issue fechada/verificada.")
    else:
        require(disposition.get("issue_state") == "open", "Adiamento/transferência preserva issue aberta.")
    if disposition['kind'] in {'deferred', 'transferred'}:
        require(text(disposition.get("owner")) and text(disposition.get("resume_condition")), "Declare dono e retomada.")
    if disposition["kind"] == "transferred":
        require(disposition.get("target") in {"bug", "improvement", "feature"} - {record["scenario"]} and text(disposition.get("target_started_evidence")), "Transferência exige destino iniciado e verificado na mesma issue.")


def validate_delivery(record, project, stage, config=None):
    require(stage in STAGES, "Etapa desconhecida.")
    fields = {"schema_version", "scenario", "issue", "roles", "owner", "implementers", "isolation", "investigation", "ui", "database", "candidate", "checks", "integration", "review", "security", "qa", "manual_test", "acceptance", "pr_draft", "pull_requests", "handoff", "blocker", "disposition", "environment", "completion"}
    require(isinstance(record, dict) and set(record) <= fields and type(record.get("schema_version")) is int and record["schema_version"] == 3, "Use schema_version 3 no registro; migre formatos anteriores com evidências reais.")
    require(text(record.get("scenario")) and record["scenario"] in {"bug", "improvement", "feature"}, "Selecione bug, improvement ou feature.")
    issue = record.get("issue")
    require(isinstance(issue, dict) and (https_reference(issue.get("url"))
            or (issue.get("url") is None and text(issue.get("scope_ref")))),
            "Informe issue real ou referência da demanda quando não houver issue.")
    contract_dir = 'agents' if (ROOT / 'agents/catalog.json').is_file() else 'contracts'
    catalog = read_json(ROOT / contract_dir / 'catalog.json')
    require(isinstance(catalog, dict) and isinstance(catalog.get("roles"), dict), "Catálogo de papéis inválido.")
    roles = record.get("roles")
    require(isinstance(roles, list) and roles and all(text(r) and r in catalog["roles"] for r in roles), "Selecione papéis existentes; humano não é agente.")
    if stage == "plan":
        return
    require(not record.get("blocker"), "Pendência ativa: registre e resolva a condição de retomada antes de avançar.")
    if stage in {"merged", "finish"}:
        require(not record.get('disposition'), "Destino sem implementação não pode encerrar como merge.")
        config = config or read_json(local_file(project, '.bezalel/project.json', 'Configuração'))
        validate_config(config)
        verify_completion(record, config, stage == 'finish')
        return
    if stage == "close":
        verify_disposition(record)
        return
    require(not record.get("disposition"), "Destino sem implementação ativo; confira a retomada antes de executar.")
    criteria = issue_criteria(issue, record["scenario"])
    if record["scenario"] == "feature":
        human_decision(issue.get("approval"), scope_subject(issue))
    if stage == 'database':
        verify_database(record.get('database'), project, scope_subject(issue), reviewing=True)
        return
    implementers = record.get("implementers")
    require(isinstance(implementers, list) and implementers and all(text(a) for a in implementers), "Identifique os devs executores.")
    require(text(record.get("owner")) and record["owner"] in implementers and DEVELOPERS.intersection(roles), "Responsável pela integração precisa ser um dev executor identificado.")
    verify_isolation(record.get("isolation"))
    if stage == "investigate":
        return
    investigation = record.get("investigation")
    passed(investigation, "Investigação")
    require(investigation.get("scope") == scope_subject(issue), "Investigação pertence a outro escopo.")
    ui = record.get("ui")
    require(isinstance(ui, dict), "Classifique interface afetada.")
    if ui.get("status") == "not_applicable":
        require(text(ui.get("reason")), "Interface não aplicável exige razão.")
    else:
        passed(ui, "UI/UX")
        independent(ui, implementers, "UI/UX")
        require(text(ui.get("mock_ref")) and ui.get("scope") == scope_subject(issue), "UI/UX exige mock/contrato e escopo atuais.")
    verify_database(record.get("database"), project, scope_subject(issue))
    if stage == "implement":
        return
    require({"coordenador", "qa", "appsec"} <= set(roles), "Aceite exige seleção de TL, QA e AppSec independentes dos autores.")
    if config is None:
        config = read_json(local_file(project, ".bezalel/project.json", "Configuração"))
    validate_config(config, project)
    candidate, subject = verify_accept_package(record, project, config, criteria)
    if stage == "accept":
        return
    if stage == 'accepted':
        verify_handoff(record, config, candidate)
        human_decision(record.get("acceptance"), subject)
        require(text(record["acceptance"].get("execution_evidence")), "Aceite exige roteiro realmente executado pelo humano.")
        return
    require(local_file(project, record.get("pr_draft"), "Rascunho de PR").stat().st_size > 0, "Rascunho de PR vazio.")
    if stage == "handoff":
        verify_handoff(record, config, candidate)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--record", required=True)
    parser.add_argument("--stage", choices=STAGES, required=True)
    args = parser.parse_args()
    project = args.project.resolve()
    try:
        config = read_json(local_file(project, ".bezalel/project.json", "Configuração"))
        validate_config(config, None if args.stage in {'merged', 'finish'} else project)
        record = read_json(local_file(project, args.record, "Registro"))
        validate_delivery(record, project, args.stage, config)
    except (ContractError, OSError, UnicodeError, TypeError, KeyError) as error:
        print(str(error) if isinstance(error, ContractError) else "Entrada/artefato inválido; conteúdo omitido.", file=sys.stderr)
        return 1
    print("Declarações consistentes para a etapa. Não comprova evidência, aprovação humana ou permissão; nenhuma ferramenta foi executada.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
