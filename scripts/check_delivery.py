#!/usr/bin/env python3
"""Validate local delivery declarations, without executing tools or granting authorization."""
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DIMENSIONS = {"files", "database", "queues", "ports", "storage"}


class ContractError(ValueError):
    """A fixed diagnostic that does not echo project content or credentials."""


def require(condition, message):
    if not condition:
        raise ContractError(message)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def local_file(project, value, label):
    require(text(value) and not Path(value).is_absolute(), label + ": informe um caminho relativo ao projeto.")
    try:
        target = (project / value).resolve()
    except (OSError, ValueError, RuntimeError):
        raise ContractError(label + ": caminho local inválido.") from None
    require(project in target.parents and target.is_file(), label + ": arquivo local ausente ou fora do projeto.")
    return target


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError):
        raise ContractError("Não foi possível ler um JSON local válido; conteúdo omitido.") from None


def validate_config(config, project=None):
    require(isinstance(config, dict), "Configuração de projeto precisa ser um objeto.")
    require(set(config) == {"schema_version", "project", "context", "interfaces", "checks", "observers"}, "Configuração contém campos ausentes/desconhecidos; não declare permissões ou credenciais aqui.")
    require(type(config["schema_version"]) is int and config["schema_version"] == 1 and text(config["project"]), "Versão/nome do projeto inválidos.")
    context = config["context"]
    require(isinstance(context, dict) and set(context) == {"architecture", "business"}, "Declare os documentos de arquitetura e negócio do projeto.")
    for value in context.values():
        require(text(value), "Referência de contexto vazia.")
        if project is not None:
            local_file(project, value, "Contexto")
    interfaces = config["interfaces"]
    require(isinstance(interfaces, list) and all(isinstance(item, str) and item in {"api", "web", "mobile"} for item in interfaces), "Interfaces inválidas.")
    checks = config["checks"]
    require(isinstance(checks, dict) and set(checks) == {"test", "lint", "build"}, "Declare test/lint/build, mesmo quando não configurados.")
    require(all(isinstance(command, list) and all(text(arg) for arg in command) for command in checks.values()), "Comandos devem ser listas de argumentos; este validador não os executa.")
    observers = config["observers"]
    require(isinstance(observers, dict) and set(observers) == {"reliability", "business"}, "Declare os dois observadores desativados.")
    for observer in observers.values():
        require(isinstance(observer, dict) and observer.get("enabled") is False and observer.get("mode") == "proposal_only", "Observadores devem permanecer desativados e somente propositivos; não há runtime de monitoramento.")
        require(type(observer.get("window_minutes")) is int and observer["window_minutes"] > 0, "Janela do observador inválida.")
    business = observers["business"]
    require(type(business.get("grace_minutes")) is int and business["grace_minutes"] >= 0, "Tolerância de negócio inválida.")
    if business.get("metric") == "check_ins":
        require(business.get("requires_scheduled_activity") is True, "Zero check-ins exige atividade prevista; não interprete ausência de calendário como zero eventos.")


def story_criteria(project, reference):
    path = local_file(project, reference, "História")
    content = path.read_text(encoding="utf-8")
    require(re.search(r"^# US-[A-Za-z0-9-]+\s+", content, re.M), "História precisa de título com ID US-.")
    sections = {}
    for heading in ["Necessidade", "Critérios observáveis", "Dependências e limites"]:
        section = re.search(r"^## " + re.escape(heading) + r"\n(.+?)(?=^## |\Z)", content, re.M | re.S)
        require(section and section[1].strip(), "História precisa de necessidade, critérios e dependências/limites explícitos.")
        sections[heading] = section[1]
    criteria = re.findall(r"^- (AC-[0-9]+):[^\S\n]+\S[^\n]*", sections["Critérios observáveis"], re.M)
    require(criteria and len(criteria) == len(set(criteria)), "Critérios precisam de IDs AC- únicos e resultados observáveis escritos.")
    return set(criteria)


def verify_isolation(isolation):
    require(isinstance(isolation, dict) and set(isolation) == DIMENSIONS, "Isolamento deve cobrir arquivos, banco, filas, portas e storage.")
    for dimension, result in isolation.items():
        require(isinstance(result, dict), "Registro de isolamento inválido.")
        if result.get("status") == "verified":
            require(text(result.get("evidence")), "Isolamento verificado exige referência de evidência.")
        else:
            require(dimension != "files" and result.get("status") == "not_applicable" and text(result.get("reason")), "Isolamento pendente/bloqueado ou não aplicável sem justificativa.")


def verify_database(database, project):
    require(isinstance(database, dict), "Declare o impacto estrutural no banco.")
    if database.get("change") == "none":
        require(text(database.get("reason")), "Banco não aplicável exige justificativa concreta.")
        require(not database.get("approval") and not database.get("proposal"), "Não registre aprovação fictícia para banco não aplicável.")
        return
    require(database.get("change") == "structural", "Impacto de banco precisa ser none ou structural.")
    proposal = local_file(project, database.get("proposal"), "Proposta de banco")
    require(proposal.stat().st_size > 0, "Proposta de banco vazia.")
    approval = database.get("approval")
    require(isinstance(approval, dict) and approval.get("decision") == "approved", "Mudança estrutural bloqueada: falta registro de aprovação humana.")
    require(approval.get("actor_type") == "human" and text(approval.get("actor")) and text(approval.get("source")), "Aprovação precisa identificar a pessoa e a fonte humana; parecer de agente não basta.")
    try:
        when = datetime.fromisoformat(approval.get("recorded_at", "").replace("Z", "+00:00"))
        require(when.tzinfo is not None, "Data da decisão precisa incluir fuso.")
    except (TypeError, AttributeError, ValueError):
        raise ContractError("Data da decisão humana inválida.") from None
    require(approval.get("proposal_sha256") == hashlib.sha256(proposal.read_bytes()).hexdigest(), "Proposta difere da versão aprovada; obtenha nova decisão humana antes de implementar.")


def passed(result, label):
    require(isinstance(result, dict) and result.get("status") == "passed" and text(result.get("evidence")), label + ": falta resultado passado com evidência.")


def validate_delivery(record, project, stage):
    require(stage in {"plan", "implement", "deliver"}, "Etapa desconhecida.")
    require(isinstance(record, dict) and type(record.get("schema_version")) is int and record["schema_version"] == 1, "Registro de entrega inválido.")
    allowed = {"schema_version", "story", "owner", "implementers", "roles", "isolation", "database", "checks", "qa", "integration", "manual_test", "pr_draft"}
    require(set(record) == allowed, "Registro tem campos ausentes/desconhecidos; não declare autorização de publicação neste arquivo.")
    criteria = story_criteria(project, record["story"])
    catalog = read_json(ROOT / "agents/catalog.json")
    require(isinstance(catalog, dict) and isinstance(catalog.get("roles"), dict), "Catálogo de papéis inválido.")
    catalog = catalog["roles"]
    roles = record["roles"]
    require(isinstance(roles, list) and roles and all(text(role) and role in catalog and isinstance(catalog[role], dict) and catalog[role].get("kind") == "delivery" for role in roles), "Selecione papéis de entrega existentes; observadores não implementam histórias.")
    if stage == "plan":
        return
    require(text(record["owner"]), "Identifique o responsável pela integração inteira.")
    implementers = record["implementers"]
    require(isinstance(implementers, list) and implementers and all(text(actor) for actor in implementers), "Identifique os implementadores antes de implementar.")
    verify_isolation(record["isolation"])
    verify_database(record["database"], project)
    if stage == "implement":
        return
    checks = record["checks"]
    require(isinstance(checks, list) and checks, "Informe verificações pertinentes e resultados, ou não aplicável justificado.")
    for check in checks:
        require(isinstance(check, dict) and text(check.get("name")), "Verificação sem nome.")
        if check.get("status") == "not_applicable":
            require(text(check.get("reason")), "Verificação não aplicável exige justificativa.")
        else:
            passed(check, "Verificação")
    qa = record["qa"]
    require(isinstance(qa, dict) and text(qa.get("reviewer")) and qa["reviewer"].strip() not in {actor.strip() for actor in implementers}, "QA precisa de identidade diferente dos implementadores.")
    results = qa.get("criteria")
    require(isinstance(results, list) and all(isinstance(item, dict) and text(item.get("id")) for item in results), "Resultados de QA inválidos.")
    require(len(results) == len(criteria) and {item["id"] for item in results} == criteria, "QA deve cobrir exatamente todos os critérios da história.")
    for result in results:
        passed(result, "Critério")
    scenarios = qa.get("additional_scenarios")
    require(isinstance(scenarios, list) and scenarios, "QA precisa de cenários adicionais derivados de requisito ou risco.")
    for scenario in scenarios:
        require(isinstance(scenario, dict) and text(scenario.get("name")) and text(scenario.get("basis")) and text(scenario.get("expected")), "Cenário adicional precisa de origem e resultado esperado.")
        passed(scenario, "Cenário adicional")
    passed(record["integration"], "Integração")
    require(record["integration"].get("owner") == record["owner"], "O responsável pela integração precisa assumir a verificação completa.")
    for key in ["manual_test", "pr_draft"]:
        require(local_file(project, record[key], key).stat().st_size > 0, "Roteiro manual/rascunho da PR não pode estar vazio.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--record", required=True)
    parser.add_argument("--stage", choices=["plan", "implement", "deliver"], required=True)
    args = parser.parse_args()
    project = args.project.resolve()
    try:
        config = read_json(local_file(project, ".bezalel/project.json", "Configuração"))
        validate_config(config, project)
        record = read_json(local_file(project, args.record, "Registro"))
        validate_delivery(record, project, args.stage)
    except (ContractError, OSError, UnicodeError) as error:
        print(str(error) if isinstance(error, ContractError) else "Falha ao ler artefatos locais; conteúdo omitido.", file=sys.stderr)
        return 1
    print("Declarações consistentes para a etapa. Não comprova evidência, aprovação humana ou permissão; nenhuma ferramenta foi executada.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
