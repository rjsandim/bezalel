#!/usr/bin/env python3
"""Check the skill package contract and integrity; --refresh updates local manifests."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import stat
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


def checksum(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    parser.add_argument("--refresh", action="store_true", help="Update current hashes; keep original provenance.")
    args = parser.parse_args()
    files = package_files()
    errors = validate_structure(files)
    inventory_path = ROOT / "inventory.json"
    inventory = json.loads(inventory_path.read_text())
    prior = {record["destination"]: record for record in inventory["files"]}
    if args.refresh and not errors:
        records = []
        for path in files:
            name = path.relative_to(ROOT).as_posix()
            record = dict(prior.get(name, {"destination": name, "kind": "new_in_bezalel"}))
            record.update(sha256=checksum(path), bytes=path.stat().st_size,
                          mode=oct(stat.S_IMODE(path.stat().st_mode)))
            if record.get("source_sha256") and record["sha256"] != record["source_sha256"]:
                note = "Adapted in Bezalel; original source hash preserved."
                record["changes"] = list(dict.fromkeys(record.get("changes", []) + [note]))
            records.append(record)
        inventory["files"] = records
        inventory_path.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n")
    actual = {path.relative_to(ROOT).as_posix(): checksum(path) for path in files}
    expected = {record["destination"]: record["sha256"] for record in inventory["files"]}
    if actual != expected:
        errors.append("Current files differ from inventory; review changes before --refresh.")
    # Include the inventory itself in SHA256SUMS; exclude only the checksum file.
    checksum_text = "".join(f"{value}  {name}\n" for name, value in sorted(actual.items()))
    checksum_text += f"{checksum(inventory_path)}  inventory.json\n"
    sums_path = ROOT / "SHA256SUMS"
    if args.refresh and not errors:
        sums_path.write_text(checksum_text)
    elif not sums_path.exists() or sums_path.read_text() != checksum_text:
        errors.append("SHA256SUMS differs from package contents.")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"Structure, local links and hashes verified: {len(actual)} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
