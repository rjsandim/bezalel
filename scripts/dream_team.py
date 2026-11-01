#!/usr/bin/env python3
"""Gera os adaptadores Codex/Claude da DreamTeam a partir do catálogo e do template único."""
import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = Path(__file__).with_name('dream-team-adapter.txt')
# Única diferença de conteúdo entre as plataformas: o arquivo de instruções do projeto.
PROJECT_INSTRUCTIONS = {'codex': 'o AGENTS.md do projeto', 'claude': 'o CLAUDE.md e o AGENTS.md do projeto'}


def quoted(value):
    """Texto de uma linha válido em TOML e no frontmatter YAML; recusa o que exigiria escape."""
    if not value or re.search(r'["\\\n]', value):
        raise ValueError('Descrição de adaptador vazia ou com caracteres que exigem escape.')
    return '"' + value + '"'


def objective(contract):
    """A descrição do adaptador é o primeiro parágrafo do Objetivo do contrato."""
    match = re.search(r'^## Objetivo\n\n(.+?)(?:\n\n|\Z)', contract, re.M | re.S)
    if not match:
        raise ValueError('Contrato sem Objetivo.')
    return ' '.join(match[1].split())


def render(root=ROOT):
    """Retorna {caminho relativo a agents/: conteúdo esperado} para os nove agentes."""
    agents = Path(root) / 'agents'
    catalog = json.loads((agents / 'catalog.json').read_text())
    flow = catalog['workflow']
    template = TEMPLATE.read_text()
    if '"""' in template or '\\' in template:
        raise ValueError('Template incompatível com string TOML multilinha.')
    result = {}
    for entry in catalog['roles'].values():
        description = quoted('DreamTeam: ' + objective((agents / entry['file']).read_text()))
        for platform in ['codex', 'claude']:
            body = template.format(display_name=entry['display_name'], contract=entry['file'],
                                   workflow=flow['source'], skills=flow['skills'],
                                   project_instructions=PROJECT_INSTRUCTIONS[platform])
            name = Path(entry[platform]).stem
            if platform == 'codex':
                content = ('name = ' + quoted(name) + '\ndescription = ' + description
                           + '\ndeveloper_instructions = """\n' + body + '"""\n')
            else:
                content = '---\nname: ' + name + '\ndescription: ' + description + '\n---\n\n' + body
            result[entry[platform]] = content
    return result


def divergent(root=ROOT):
    """Adaptadores do catálogo ausentes ou diferentes do gerado."""
    agents = Path(root) / 'agents'
    return [name for name, content in render(root).items()
            if not (agents / name).is_file() or (agents / name).read_text() != content]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['generate', 'check'])
    args = parser.parse_args()
    try:
        if args.action == 'check':
            names = divergent()
            for name in names:
                print('Adaptador diverge do gerado: agents/' + name, file=sys.stderr)
            return 1 if names else 0
        for name, content in render().items():
            path = ROOT / 'agents' / name
            if not path.is_file() or path.read_text() != content:
                path.write_text(content)
                print('Atualizado: agents/' + name)
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print('Não foi possível gerar os adaptadores: ' + str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
