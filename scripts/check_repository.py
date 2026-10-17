#!/usr/bin/env python3
"""Check skill structure, essential metadata and local links without changing files."""
import argparse
from pathlib import Path
import re
import sys
import tomllib
import zipfile
from xml.etree import ElementTree
from check_delivery import ContractError, local_file, read_json, require, text, validate_config

ROOT = Path(__file__).resolve().parents[1]
SECTIONS = ["Objetivo e escopo", "Entradas e pré-requisitos", "Procedimento", "Saídas", "Validação", "Limites operacionais"]
# Exceções de formato autorizadas no AGENTS.md; demais verificações permanecem.
UPSTREAM_FORMAT_SKILLS = {
    "security-audit", "humanizer", "verification-planning", "agent-browser",
    "release", "reflect", "github-resolution", "pr-bump", "pr-post-audit",
}
EXCLUDED = {".git", ".DS_Store", "__pycache__", "state", "backups", ".local-review", ".pytest_cache"}


def package_files():
    candidates = [ROOT / name for name in ["README.md", "AGENTS.md", ".gitignore", ".bezalel/.gitignore", ".bezalel/project.example.json", ".bezalel/upstream.json"]]
    for directory in [ROOT / "skills", ROOT / "scripts", ROOT / "agents", ROOT / "tests", ROOT / '.github']:
        candidates.extend(directory.rglob("*"))
    return sorted(p for p in candidates if p.is_file()
                  and not any(part in EXCLUDED for part in p.relative_to(ROOT).parts)
                  and not p.name.endswith((".pyc", ".local.json")))


def has_skill_description(frontmatter):
    """Aceita descrição em linha ou bloco YAML com conteúdo, sem executar YAML."""
    match = re.search(r"^description: ([^\n]+)$", frontmatter, re.M)
    if not match:
        return False
    value = match[1].strip()
    if value not in {"|", "|-", "|+", ">", ">-", ">+"}:
        return bool(value and value not in {"''", '\"\"'})
    for line in frontmatter[match.end():].splitlines():
        if not line.strip():
            continue
        if not line[0].isspace():
            return False
        if not line.lstrip().startswith("#"):
            return True
    return False


def validate_structure(files):
    errors = []
    for directory in sorted((ROOT / "skills").iterdir()):
        if not directory.is_dir():
            continue
        entry = directory / "SKILL.md"
        if not entry.exists():
            errors.append(f"Missing SKILL.md: {directory.name}")
            continue
        text = entry.read_text()
        front = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
        if not front or not re.search(r"^name: " + re.escape(directory.name) + r"$", front[1], re.M) or not has_skill_description(front[1]):
            errors.append(f"Invalid essential metadata: {directory.name}")
        if directory.name not in UPSTREAM_FORMAT_SKILLS and re.findall(r"^## (.+)$", text, re.M) != SECTIONS:
            errors.append(f"Unexpected section order: {directory.name}")
    for path in files:
        if path.suffix != ".md":
            continue
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
            if target.startswith(("http://", "https://", "#")):
                continue
            resolved = (path.parent / target.split("#", 1)[0]).resolve()
            if not resolved.exists() or ROOT not in resolved.parents:
                errors.append(f"Missing/outside link in {path.relative_to(ROOT)}: {target}")
    return errors


def validate_agents():
    headings = ["Objetivo", "Entradas", "Saídas", "Ferramentas necessárias", "Limites e permissões", "Critérios de pronto", "Seleção de skills", "Contrato de handoff"]
    expected_roles = {"produto", "coordenador", "infraestrutura", "dev-fullstack", "backend", "frontend-web", "mobile", "qa", "appsec"}
    try:
        catalog = read_json(ROOT / "agents/catalog.json")
        require(isinstance(catalog, dict) and set(catalog) == {"schema_version", "execution", "company_flow", "roles", "external_actors"}, "Catálogo v2 inválido.")
        require(catalog["schema_version"] == 2 and catalog["execution"] == "agent_contracts", "Catálogo não pode declarar runtime implementado.")
        require(isinstance(catalog["roles"], dict) and set(catalog["roles"]) == expected_roles, "Catálogo deve conter os nove agentes ativos da v2, incluindo AppSec.")
        flow = catalog["company_flow"]
        source = local_file(ROOT / "agents", flow["source"], "Fluxo").read_text()
        require(re.findall(r"^### (R\d+) ", source, re.M) == ["R" + str(n) for n in range(1, 11)], "Preserve as dez regras comuns da v2.")
        local_file(ROOT / "agents", flow["skills"], "Relação de skills")
        sections = {}
        for block in re.split(r"^### ", source, flags=re.M):
            match = re.search(r"\*\*Referência:\*\* `([^`]+)`\. \*\*Responsável:\*\* ([^\n]+)\.", block)
            if match:
                require(match[1] not in sections, "Processo duplicado no fluxo.")
                procedure = block.split("**Pronto:**", 1)[0]
                require(re.findall(r"^([123])\. \*\*", procedure, re.M) == ["1", "2", "3"], "Cada processo v2 deve preservar suas três etapas.")
                sections[match[1]] = (match[2], procedure)
        require(len(sections) == 20, "O fluxo deve cobrir os 20 processos da v2.")
        scenarios = flow["scenarios"]
        require(isinstance(scenarios, list) and len(scenarios) == 3 and len({x["id"] for x in scenarios}) == 3, "Declare três cenários distintos.")
        require(text(flow["company_id"]) and type(flow["revision"]) is int, "Declare empresa e revisão visual conferidas.")
        actors = catalog["external_actors"]
        require(isinstance(actors, dict) and set(actors) == {"aprovador-humano"}, "Mantenha o humano externo ao catálogo de agentes.")
        skills_available = {p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")}
        declared, adapters, claude_adapters, process_keys, process_ids, role_ids = set(), set(), set(), [], [], []
        for role, entry in {**catalog["roles"], **actors}.items():
            human = role in actors
            require(isinstance(entry, dict) and entry["kind"] == ("human" if human else "delivery"), "Tipo de papel inválido.")
            path = local_file(ROOT / "agents", entry["file"], "Contrato")
            require(path.parent == ROOT / "agents" / ("actors" if human else "roles"), "Contrato fora da pasta prevista.")
            content = path.read_text()
            require(text(entry["display_name"]) and re.search(r"^# " + re.escape(entry["display_name"]) + r"$", content, re.M), "Nome de apresentação diverge do contrato.")
            role_ids.append(entry["company_flow_role_id"])
            required_skills = set()
            require(isinstance(entry["processes"], list) and entry["processes"], "Papel sem processos.")
            for process in entry["processes"]:
                key = process["key"]
                require(key in sections and sections[key][0] == entry["display_name"], "Processo atribuído ao responsável incorreto.")
                require('#process-' + key in content, "Contrato não referencia seu processo.")
                found_skills = {skill for skill in skills_available if re.search(r"(?<![a-z-])" + re.escape(skill) + r"(?![a-z-])", sections[key][1])}
                require(isinstance(process["skills"], list) and len(process["skills"]) == len(set(process["skills"])) and set(process["skills"]) == found_skills, "Skills do catálogo divergem do procedimento.")
                required_skills.update(found_skills)
                process_keys.append(key)
                process_ids.append(process["id"])
            if human:
                require(not required_skills and 'codex' not in entry and 'claude' not in entry, "Humano não recebe skills ou adaptador de agente.")
                continue
            declared.add(path)
            require(re.search(r"^role: " + re.escape(role) + r"$", content, re.M) and re.search(r"^kind: delivery$", content, re.M), "Metadados do papel divergentes.")
            require(re.findall(r"^## (.+)$", content, re.M) == headings, "Seções de papel incompletas.")
            require(set(entry["skills"]) == required_skills, "Seleção de skills do papel diverge das etapas.")
            require(all('../../skills/' + skill + '/SKILL.md' in content for skill in required_skills), "Skill ausente do contrato.")
            adapter_path = local_file(ROOT / "agents", entry["codex"], "Adaptador Codex")
            require(adapter_path.parent == ROOT / "agents/codex", "Adaptador fora da pasta prevista.")
            adapters.add(adapter_path)
            adapter = tomllib.loads(adapter_path.read_text())
            require(set(adapter) == {"name", "description", "developer_instructions"} and adapter["name"] == 'bezalel-' + role and text(adapter["description"]), "Adaptador inválido ou amplia configurações não previstas.")
            require('agents/' + entry["file"] in adapter["developer_instructions"] and 'agents/company-flow-v2.md' in adapter["developer_instructions"], "Adaptador precisa carregar contrato e fluxo vigentes.")
            claude_path = local_file(ROOT / "agents", entry["claude"], "Adaptador Claude")
            require(claude_path.parent == ROOT / 'agents/claude', "Adaptador Claude fora da pasta prevista.")
            claude_adapters.add(claude_path)
            claude = claude_path.read_text()
            require(claude.startswith('---\nname: bezalel-' + role + '\ndescription: ') and claude.count('\n---\n') == 1, "Adaptador Claude inválido.")
            front, body = claude[4:].split('\n---\n', 1)
            require(len(front.splitlines()) == 2 and text(front.splitlines()[1].removeprefix('description: ').strip('"')), "Adaptador Claude amplia configurações não previstas.")
            require('agents/' + entry['file'] in body and 'agents/company-flow-v2.md' in body, "Adaptador Claude deve carregar contrato e fluxo.")
        require(len(role_ids) == len(set(role_ids)) == 10, "Identidades dos cargos duplicadas.")
        require(len(process_keys) == len(set(process_keys)) == 20 and set(process_keys) == set(sections), "Processo órfão ou duplicado no catálogo.")
        require(len(process_ids) == len(set(process_ids)) == 20, "IDs de processos duplicados.")
        require(declared == set((ROOT / "agents/roles").glob("*.md")), "Contrato de agente órfão.")
        require(adapters == set((ROOT / "agents/codex").glob("*.toml")), "Adaptador de agente órfão.")
        require(claude_adapters == set((ROOT / 'agents/claude').glob('*.md')), "Adaptador Claude órfão.")
        validate_config(read_json(ROOT / ".bezalel/project.example.json"))
    except ContractError as error:
        return [str(error)]
    except (OSError, UnicodeError, TypeError, ValueError, KeyError, AttributeError):
        return ["Não foi possível validar catálogo, contratos ou adaptadores; conteúdo omitido."]
    return []


def validate_upstream():
    """Valida a seleção de atualização, sem proibir customizações locais detectáveis."""
    try:
        manifest = read_json(ROOT / '.bezalel/upstream.json')
        require(manifest['schema_version'] == 1 and manifest['repository'] == 'https://github.com/akitaonrails/my-skills.git', 'Origem de skills inválida.')
        require(set(manifest['skills']) == UPSTREAM_FORMAT_SKILLS, 'Seleção automática diverge das nove importações preservadas.')
        require(set(manifest['excluded_adaptations']) == {'pr-audit', 'iss-audit'}, 'Auditorias adaptadas devem ficar protegidas.')
        for name, entry in manifest['skills'].items():
            require(re.fullmatch('[a-f0-9]{40}', entry['revision']) is not None, 'Revisão upstream inválida.')
            require('SKILL.md' in entry['files'], 'Origem sem skill principal.')
            for path, record in entry['files'].items():
                require(not Path(path).is_absolute() and '..' not in Path(path).parts, 'Origem com caminho externo.')
                require(re.fullmatch('[a-f0-9]{64}', record['sha256']) is not None and record['mode'] in {0o644, 0o755}, 'Registro de origem inválido.')
            require(set(entry['preserve']) <= {'agents/openai.yaml'}, 'Overlay upstream não autorizado.')
            require(all(path in entry['files'] for path in entry['preserve']), 'Overlay sem origem conhecida.')
    except (ContractError, OSError, ValueError, KeyError, TypeError):
        return ['Manifesto de atualização upstream inválido.']
    return []


def validate_workbook_template(path=None):
    """Check the packaged empty template without requiring a spreadsheet runtime."""
    path = path or ROOT / "skills/development-test-workbook/assets/test-plan-template.xlsx"
    expected = ["Resumo", "Guia de execução", "Casos de teste", "Dados do ambiente", "Consultas SQL", "Backlog"]
    namespace = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    try:
        with zipfile.ZipFile(path) as archive:
            if archive.testzip() is not None:
                return ["Template Excel corrompido."]
            workbook = ElementTree.fromstring(archive.read("xl/workbook.xml"))
            sheets = workbook.findall("s:sheets/s:sheet", namespace)
            if [sheet.get("name") for sheet in sheets] != expected:
                return ["Abas do template Excel divergem do contrato."]
            for name in archive.namelist():
                if "vbaProject" in name or name.startswith("xl/externalLinks/"):
                    return ["Template Excel contém macro ou vínculo externo."]
                if name.endswith(".rels"):
                    relationships = ElementTree.fromstring(archive.read(name))
                    if any(rel.get("TargetMode") == "External" for rel in relationships):
                        return ["Template Excel contém relacionamento externo."]
    except (OSError, KeyError, zipfile.BadZipFile, ElementTree.ParseError):
        return ["Template Excel ausente ou inválido."]
    return []


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    files = package_files()
    errors = validate_structure(files) + validate_agents() + validate_upstream() + validate_workbook_template()
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("Estrutura, catálogo de papéis, configuração de exemplo, metadados, links locais e template Excel verificados.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
