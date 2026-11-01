#!/usr/bin/env python3
"""Gera os adaptadores Codex/Claude e o índice de processos da DreamTeam a partir do catálogo."""
import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = 'scripts/dream-team-adapter.txt'
# Única diferença de conteúdo entre as plataformas: o arquivo de instruções do projeto.
PROJECT_INSTRUCTIONS = {'codex': 'o AGENTS.md do projeto', 'claude': 'o CLAUDE.md e o AGENTS.md do projeto'}
INDEX = '## Índice de processos\n'
REFERENCE = re.compile(r'\*\*Referência:\*\* `([^`]+)`\. \*\*Responsável:\*\* ([^\n]+)\.')
STEP = re.compile(r'^([123])\. (\*\*[^*]+\*\*)', re.M)


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


def mentions(skill, content):
    return re.search(r'(?<![a-z-])' + re.escape(skill) + r'(?![a-z-])', content) is not None


def processes(catalog):
    """Processos na ordem do catálogo: papéis e depois o aprovador humano externo."""
    return [process for entry in [*catalog['roles'].values(), *catalog['external_actors'].values()]
            for process in entry['processes']]


def render(root=ROOT):
    """Retorna {caminho relativo a agents/: conteúdo esperado} para os nove agentes."""
    agents = Path(root) / 'agents'
    catalog = json.loads((agents / 'catalog.json').read_text())
    flow = catalog['workflow']
    template = (Path(root) / TEMPLATE).read_text()
    if '"""' in template or '\\' in template:
        raise ValueError('Template incompatível com string TOML multilinha.')
    result = {}
    for entry in catalog['roles'].values():
        description = quoted('DreamTeam: ' + objective((agents / entry['file']).read_text()))
        assigned = ', '.join('agents/' + process['file'] for process in entry['processes'])
        for platform in ['codex', 'claude']:
            body = template.format(display_name=entry['display_name'], contract=entry['file'],
                                   workflow=flow['source'], skills=flow['skills'], processes=assigned,
                                   project_instructions=PROJECT_INSTRUCTIONS[platform])
            name = Path(entry[platform]).stem
            if platform == 'codex':
                content = ('name = ' + quoted(name) + '\ndescription = ' + description
                           + '\ndeveloper_instructions = """\n' + body + '"""\n')
            else:
                content = '---\nname: ' + name + '\ndescription: ' + description + '\n---\n\n' + body
            result[entry[platform]] = content
    return result


def render_index(root=ROOT):
    """Índice de consulta com título, responsável, etapas e skills de cada processo.

    Mantém em `dream-team.md` os blocos que o checker de versões anteriores confere ao
    atualizar instalações existentes; o procedimento completo fica no arquivo do processo.
    """
    agents = Path(root) / 'agents'
    catalog = json.loads((agents / 'catalog.json').read_text())
    lines = [INDEX, 'Gerado por `scripts/dream_team.py` a partir dos arquivos de processo; não edite à mão.',
             'Lista os processos por responsável, na ordem do catálogo, com as skills de cada etapa.',
             'Serve para consulta; cada papel lê somente os arquivos dos processos atribuídos.',
             'As âncoras preservam os links `' + catalog['workflow']['source'] + '#process-<referência>`.', '']
    for process in processes(catalog):
        content = (agents / process['file']).read_text()
        title = re.search(r'^# (.+)$', content, re.M)[1]
        key, owner = REFERENCE.search(content).groups()
        procedure = content.split('**Pronto:**', 1)[0]
        steps = re.split(r'^[123]\. ', procedure, flags=re.M)[1:]
        lines += ['<a id="process-' + key + '"></a>', '', '### ' + title, '',
                  '**Referência:** `' + key + '`. **Responsável:** ' + owner + '.', '',
                  'Procedimento: [' + process['file'] + '](' + process['file'] + ').', '']
        for (number, heading), step in zip(STEP.findall(procedure), steps):
            used = [skill for skill in process['skills'] if mentions(skill, step)]
            lines.append(number + '. ' + heading + (' Skills: ' + ', '.join(used) + '.' if used else ''))
        lines.append('')
    return '\n'.join(lines)


def expected_files(root=ROOT):
    """Adaptadores e fluxo com o índice regenerado, relativos a agents/."""
    agents = Path(root) / 'agents'
    flow = json.loads((agents / 'catalog.json').read_text())['workflow']['source']
    source = (agents / flow).read_text()
    if source.count(INDEX) != 1:
        raise ValueError('Fluxo sem seção única de índice de processos.')
    return {**render(root), flow: source.split(INDEX, 1)[0] + render_index(root)}


def divergent(root=ROOT):
    """Arquivos gerados ausentes ou diferentes do esperado."""
    agents = Path(root) / 'agents'
    return [name for name, content in expected_files(root).items()
            if not (agents / name).is_file() or (agents / name).read_text() != content]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['generate', 'check'])
    args = parser.parse_args()
    try:
        if args.action == 'check':
            names = divergent()
            for name in names:
                print('Arquivo diverge do gerado: agents/' + name, file=sys.stderr)
            return 1 if names else 0
        for name, content in expected_files().items():
            path = ROOT / 'agents' / name
            if not path.is_file() or path.read_text() != content:
                path.write_text(content)
                print('Atualizado: agents/' + name)
        return 0
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        print('Não foi possível gerar os arquivos da DreamTeam: ' + str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
