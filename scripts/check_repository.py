#!/usr/bin/env python3
"""Check skill structure, essential metadata and local links without changing files."""
import argparse
from pathlib import Path
import re
import sys
from check_delivery import ContractError, local_file, read_json, require, text, validate_config

ROOT = Path(__file__).resolve().parents[1]
SECTIONS = ["Objetivo e escopo", "Entradas e pré-requisitos", "Procedimento", "Saídas", "Validação", "Limites operacionais"]
EXCLUDED = {".git", ".DS_Store", "__pycache__", "state", "backups", ".local-review", ".pytest_cache"}


def package_files():
    candidates = [ROOT / name for name in ["README.md", "AGENTS.md", ".gitignore", ".bezalel/.gitignore", ".bezalel/project.example.json"]]
    for directory in [ROOT / "skills", ROOT / "scripts", ROOT / "agents", ROOT / "tests"]:
        candidates.extend(directory.rglob("*"))
    return sorted(p for p in candidates if p.is_file()
                  and not any(part in EXCLUDED for part in p.relative_to(ROOT).parts)
                  and not p.name.endswith((".pyc", ".local.json")))


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
        if not front or not re.search(r"^name: " + re.escape(directory.name) + r"$", front[1], re.M) or not re.search(r"^description: \S.+$", front[1], re.M):
            errors.append(f"Invalid essential metadata: {directory.name}")
        if re.findall(r"^## (.+)$", text, re.M) != SECTIONS:
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
    errors = []
    headings = ["Objetivo", "Entradas", "Saídas", "Ferramentas necessárias", "Limites e permissões", "Critérios de pronto", "Seleção de skills", "Contrato de handoff"]
    try:
        catalog = read_json(ROOT / "agents/catalog.json")
        if not isinstance(catalog, dict) or type(catalog.get("schema_version")) is not int or catalog.get("schema_version") != 1 or catalog.get("execution") != "definitions_only" or not isinstance(catalog.get("roles"), dict):
            return ["Catálogo de papéis inválido ou declara execução não implementada."]
        declared = set()
        for role, entry in catalog["roles"].items():
            if not isinstance(entry, dict) or entry.get("kind") not in {"delivery", "observer"}:
                errors.append("Tipo de papel inválido no catálogo.")
                continue
            path = (ROOT / "agents" / entry.get("file", "")).resolve()
            if path.parent != ROOT / "agents/roles" or not path.is_file():
                errors.append("Arquivo de papel ausente ou fora de agents/roles.")
                continue
            declared.add(path)
            content = path.read_text()
            if not text(entry.get("display_name")) or not re.search(r"^# " + re.escape(entry["display_name"]) + r"$", content, re.M):
                errors.append("Nome de apresentação diverge do contrato: " + role)
            if not re.search(r"^role: " + re.escape(role) + r"$", content, re.M) or not re.search(r"^kind: " + entry["kind"] + r"$", content, re.M):
                errors.append("Metadados do papel divergem do catálogo: " + role)
            if re.findall(r"^## (.+)$", content, re.M) != headings:
                errors.append("Seções de papel incompletas: " + role)
            skills = entry.get("skills")
            if not isinstance(skills, list) or any(not isinstance(skill, str) or not (ROOT / "skills" / skill / "SKILL.md").is_file() for skill in skills):
                errors.append("Seleção de skills inválida: " + role)
        if declared != set((ROOT / "agents/roles").glob("*.md")):
            errors.append("Há papéis fora do catálogo ou referências duplicadas/incompletas.")
        config = read_json(ROOT / ".bezalel/project.example.json")
        validate_config(config)
        responsibilities = catalog.get("responsibilities")
        require(isinstance(responsibilities, dict) and set(responsibilities) == {"reliability", "business"}, "Declare as responsabilidades de observação.")
        for name, entry in responsibilities.items():
            require(isinstance(entry, dict) and entry.get("enabled") is False and entry.get("mode") == "proposal_only", "Responsabilidade de observação deve permanecer desativada e propositiva.")
            require(isinstance(entry.get("owner_role"), str) and entry["owner_role"] in catalog["roles"], "Responsabilidade sem papel proprietário válido.")
            local_file(ROOT / "agents", entry.get("file"), "Responsabilidade")
            require(config["observers"][name].get("owner_role") == entry["owner_role"], "Dono da observação diverge entre catálogo e exemplo de projeto.")
        actors = catalog.get("external_actors")
        require(isinstance(actors, dict) and "aprovador-humano" in actors, "Declare o aprovador humano externo.")
        for actor, entry in actors.items():
            require(actor not in catalog["roles"] and isinstance(entry, dict) and entry.get("kind") == "human", "Ator humano não pode ser papel de agente.")
            require(text(entry.get("display_name")), "Ator externo sem nome.")
            local_file(ROOT / "agents", entry.get("file"), "Ator externo")
    except (ContractError, OSError, UnicodeError, TypeError, ValueError):
        errors.append("Não foi possível validar catálogo/configuração de exemplo.")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    files = package_files()
    errors = validate_structure(files) + validate_agents()
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("Estrutura, catálogo de papéis, configuração de exemplo, metadados e links locais verificados.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
