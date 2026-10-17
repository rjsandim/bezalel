#!/usr/bin/env python3
"""Empacota plugins nativos e conecta seus contratos ao projeto consumidor."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

from distribution import DistributionError, atomic_write, files, git, inside, json_bytes, read_json
from project import apply, desired, lock, plan

ROOT = Path(__file__).resolve().parents[1]
STATE = '.bezalel/plugin.local.json'
MARKETPLACE = 'bezalel'


def build(source, output):
    source, output = Path(source).resolve(), Path(output).absolute()
    if output.exists() or output.is_symlink():
        raise DistributionError('O destino do pacote deve ser novo; não sobrescrevemos um plugin instalado.')
    content = {}
    for directory in ['skills', 'agents']:
        for name, value in files(source / directory).items():
            content[('contracts' if directory == 'agents' else directory) + '/' + name] = value
    for script in ['distribution.py', 'project.py', 'plugin.py']:
        content['scripts/' + script] = ((source / 'scripts' / script).read_bytes(), 0o644)
    for name in ['.bezalel/project.example.json']:
        content[name] = ((source / name).read_bytes(), 0o644)
    hasher = hashlib.sha256()
    for name, (data, mode) in sorted(content.items()):
        hasher.update(json_bytes([name, mode, len(data)]))
        hasher.update(data)
    version = '2.0.0-' + hasher.hexdigest()[:16]
    catalog = read_json(source / 'agents/catalog.json')
    entries = desired(source, source, ['claude'], False)
    commands = []
    for path, entry in entries.items():
        if path.startswith('.claude/commands/'):
            name = 'commands/' + Path(path).name
            body = entry['content'].replace('`.bezalel/base/', '`${CLAUDE_PLUGIN_ROOT}/')
            content[name] = (body.encode(), 0o644)
            commands.append('./' + name)
    manual = {Path(p).stem.removeprefix('bezalel-') for p in commands}
    skills = ['./skills/' + p.name for p in sorted((source / 'skills').iterdir())
              if (p / 'SKILL.md').is_file() and p.name not in manual]
    # Apenas os adaptadores são carregados como agentes; contratos não são prompts nativos.
    for entry in catalog['roles'].values():
        for platform in ['codex', 'claude']:
            path = 'contracts/' + entry[platform]
            content[path] = (content[path][0].replace(b'agents/', b'contracts/'), 0o644)
        path = 'contracts/' + entry['claude']
        body = content[path][0].decode().replace(
            'Localize a base em .bezalel/base no projeto consumidor; nesta árvore do Bezalel, use a raiz atual.',
            'Use ${CLAUDE_PLUGIN_ROOT} como raiz da base instalada. Leia o contexto do projeto consumidor.')
        content[path] = (body.encode(), 0o644)
    identity = {'name': 'bezalel', 'version': version,
                'description': 'Plugin Bezalel com a equipe DreamTeam, fluxo de desenvolvimento e skills.'}
    def hook(client, variable):
        return {'hooks': {'SessionStart': [{'matcher': 'startup', 'hooks': [{
            'type': 'command', 'command': 'python3 "${' + variable + '}/scripts/plugin.py" refresh --client ' + client,
            'timeout': 60}]}]}}
    codex_hook, claude_hook = hook('codex', 'PLUGIN_ROOT'), hook('claude', 'CLAUDE_PLUGIN_ROOT')
    manifests = {
        'plugin.json': {'$schema': 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json', **identity,
                        'extensions': {'com.openai': {'hooks': './hooks/codex.json',
                        'interface': {'displayName': 'Bezalel', 'shortDescription': identity['description'],
                                      'developerName': 'Bezalel', 'category': 'Productivity'}}}},
        '.codex-plugin/plugin.json': {**identity, 'skills': './skills/', 'hooks': './hooks/codex.json'},
        '.claude-plugin/plugin.json': {**identity, 'author': {'name': 'Bezalel'},
            'agents': ['./contracts/' + entry['claude'] for entry in catalog['roles'].values()],
            'skills': skills, 'commands': commands, 'hooks': './hooks/claude.json'},
        '.agents/plugins/marketplace.json': {'name': MARKETPLACE, 'interface': {'displayName': 'Bezalel'},
            'plugins': [{'name': 'bezalel', 'source': {'source': 'local', 'path': './'},
                         'policy': {'installation': 'AVAILABLE', 'authentication': 'ON_INSTALL'}, 'category': 'Productivity'}]},
        '.claude-plugin/marketplace.json': {'name': MARKETPLACE, 'description': identity['description'], 'owner': {'name': 'Bezalel'},
            'plugins': [{'name': 'bezalel', 'source': './', 'description': identity['description']}]},
        'hooks/codex.json': codex_hook, 'hooks/claude.json': claude_hook,
    }
    for name, value in manifests.items():
        content[name] = (json_bytes(value), 0o644)
    content['README.md'] = (('\n'.join([
        '# Bezalel para Codex e Claude Code', '',
        'Bezalel é o plugin; DreamTeam é sua equipe de nove agentes de desenvolvimento.',
        'Pacote gerado. Não edite este cache: altere a fonte e publique uma nova revisão.',
        'Os contratos portáteis ficam em [contracts/README.md](contracts/README.md).',
        'As skills originais são preservadas. Os agentes nativos carregam seus contratos.',
        '', '## Como adotar o Bezalel em um projeto', '',
        'Depois de instalar, conecte o projeto com:', '',
        '```sh',
        'python3 "/caminho/do/plugin/scripts/plugin.py" enable --project "/caminho/do/projeto" --client both',
        '```', '',
        'Use o caminho realmente instalado mostrado pelo aplicativo. Preencha o contexto do projeto.',
        'Leia o [guia da fonte](https://github.com/rjsandim/bezalel#readme) para instalação,',
        'atualização, confiança nos hooks e limites de suporte.', '',
    ])).encode(), 0o644)
    try:
        output.mkdir(parents=True)
        for name, (data, mode) in content.items():
            atomic_write(inside(output, name), data, mode)
    except BaseException:
        if output.is_dir():
            shutil.rmtree(output)
        raise
    return version


def bind(project, root, state, clients, automatic):
    direct = project / '.bezalel/install.local.json'
    if direct.is_file() and read_json(direct).get('enabled'):
        raise DistributionError('Desligue a integração direta antes de conectar o plugin; evite duas cópias ativas.')
    # Skills e agentes Claude vêm do loader do plugin. Codex recebe TOMLs por projeto.
    entries = desired(project, root, ['codex'] if 'codex' in clients else [], False, contract_dir='contracts')
    entries = {p: entry for p, entry in entries.items() if not p.startswith('.agents/skills/')}
    if 'claude' in clients:
        entries['CLAUDE.md'] = entries['AGENTS.md']
    entries['.bezalel/base'] = {'kind': 'link', 'target': str(root.resolve())}
    entries['README.md'] = {'kind': 'block', 'content': '\n'.join([
        '## Bezalel neste projeto', '',
        'Plugin `bezalel@bezalel`; contratos e origem carregada em `.bezalel/base`.',
        'Contexto próprio: `.bezalel/project.json`. Não edite o cache do plugin.',
        'A atualização usa os comandos nativos e passa a valer em uma nova sessão.',
        'Para desligar esta conexão: `python3 .bezalel/base/scripts/plugin.py disable --project .`.',
        'Atualização automática: ' + ('ligada.' if automatic else 'desligada.'),
    ])}
    changes, managed = plan(project, state.get('managed', {}), entries)
    new = {'schema_version': 1, 'enabled': True, 'clients': clients, 'automatic': automatic,
           'version': read_json(root / 'plugin.json')['version'], 'managed': managed}
    changes[STATE] = {'kind': 'file', 'content': json_bytes(new).decode()}
    context = inside(project, '.bezalel/project.json')
    if not context.exists():
        changes['.bezalel/project.json'] = {'kind': 'file', 'content': (root / '.bezalel/project.example.json').read_text()}
    ignore = inside(project, '.bezalel/.gitignore')
    text = ignore.read_text() if ignore.exists() else ''
    extra = [p for p in ['/base', '/plugin.local.json', '/update.lock', '/vps-deploy.local.json'] if p not in text.splitlines()]
    if extra:
        changes['.bezalel/.gitignore'] = {'kind': 'file', 'content': text.rstrip('\n') + '\n' + '\n'.join(extra) + '\n'}
    apply(project, changes)
    return new


def refresh_commands(client):
    if client == 'codex':
        return [['codex', 'plugin', 'marketplace', 'upgrade', MARKETPLACE],
                ['codex', 'plugin', 'add', 'bezalel@' + MARKETPLACE]]
    if client == 'claude':
        return [['claude', 'plugin', 'marketplace', 'update', MARKETPLACE],
                ['claude', 'plugin', 'update', 'bezalel@' + MARKETPLACE, '--scope', 'project']]
    raise DistributionError('Aplicativo não suportado.')


def check_runtime_state(root):
    """Caches nativos são substituíveis; não descarte estado de ambientes/backup."""
    for name in ['state', 'backups']:
        for path in (root / 'skills').glob('*/' + name):
            if path.is_dir() and any(path.iterdir()):
                raise DistributionError('Há estado operacional no plugin. Preserve/migre esse estado antes de atualizar; prefira a integração direta para ENV.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['build', 'enable', 'disable', 'refresh'])
    parser.add_argument('--output', type=Path)
    parser.add_argument('--project', type=Path, default=Path.cwd())
    parser.add_argument('--client', choices=['codex', 'claude', 'both'], default='both')
    parser.add_argument('--no-auto-update', action='store_true')
    args = parser.parse_args()
    try:
        if args.action == 'build':
            if not args.output:
                raise DistributionError('Informe um diretório novo em --output.')
            print('Plugin preparado: ' + build(ROOT, args.output))
            return 0
        try:
            project = Path(git(args.project, 'rev-parse', '--show-toplevel').decode().strip()).resolve()
        except DistributionError:
            if args.action == 'refresh':
                return 0
            raise
        state_path = inside(project, STATE)
        if args.action == 'refresh' and not state_path.is_file():
            return 0
        with lock(project):
            state = read_json(state_path) if state_path.is_file() else {}
            if state and state.get('schema_version') != 1:
                raise DistributionError('Registro de plugin incompatível.')
            if args.action == 'enable':
                clients = ['codex', 'claude'] if args.client == 'both' else [args.client]
                bind(project, ROOT, state, clients, not args.no_auto_update)
                print('Plugin conectado ao projeto. Preencha o contexto e reabra a sessão.')
            elif args.action == 'disable':
                changes, _ = plan(project, state.get('managed', {}), {})
                changes[STATE] = {'kind': 'file', 'content': json_bytes({'schema_version': 1, 'enabled': False}).decode()}
                apply(project, changes)
                print('Conexão desligada; desabilite também o plugin no aplicativo se não quiser suas skills disponíveis.')
            else:
                if not state.get('enabled') or args.client not in state['clients']:
                    return 0
                # Reaponta contratos/adaptadores somente para a versão carregada pelo aplicativo.
                changed = state['version'] != read_json(ROOT / 'plugin.json')['version']
                bind(project, ROOT, state, state['clients'], state['automatic'])
                if state['automatic']:
                    check_runtime_state(ROOT)
                    for command in refresh_commands(args.client):
                        subprocess.run(command, cwd=project, check=True, timeout=25,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if changed:
                    print(json_bytes({'hookSpecificOutput': {'hookEventName': 'SessionStart',
                          'additionalContext': 'Bezalel: contratos e agentes atualizados. Reabra a sessão para carregar os novos TOMLs do Codex.'}}).decode(), end='')
        return 0
    except (DistributionError, OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print('Bezalel plugin: ' + (str(error) if isinstance(error, DistributionError)
              else 'atualização/conexão não concluída; confira a instalação no aplicativo. Saídas privadas omitidas.'), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
