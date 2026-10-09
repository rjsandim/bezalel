#!/usr/bin/env python3
"""Check skill structure, essential metadata and local links without changing files."""
import argparse
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SECTIONS = ["Objetivo e escopo", "Entradas e pré-requisitos", "Procedimento", "Saídas", "Validação", "Limites operacionais"]
EXCLUDED = {".git", ".DS_Store", "__pycache__", "state", "backups", ".local-review", ".pytest_cache"}


def package_files():
    candidates = [ROOT / name for name in ["README.md", "AGENTS.md", ".gitignore", ".bezalel/.gitignore"]]
    for directory in [ROOT / "skills", ROOT / "scripts"]:
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    files = package_files()
    errors = validate_structure(files)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("Estrutura, metadados essenciais e links locais verificados.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
