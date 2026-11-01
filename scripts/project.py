#!/usr/bin/env python3
"""Liga, atualiza ou desliga o Bezalel por projeto, preservando customizações."""
import argparse
import contextlib
import fcntl
import io
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile

from distribution import (DistributionError, atomic_write, digest, git, inside,
                          json_bytes, read_json)

ROOT = Path(__file__).resolve().parents[1]
STATE = '.bezalel/install.local.json'
START, END = '<!-- bezalel:begin -->', '<!-- bezalel:end -->'
# A base fica no checkout principal; em worktrees o hook a atualiza e liga a worktree atual.
HOOK_COMMAND = ('r="$(git worktree list --porcelain | sed -n \'1s/^worktree //p\')"; '
                's="$r/.bezalel/base/scripts/project.py"; '
                '[ ! -f "$s" ] || python3 "$s" update --project "$r" --hook')
LEGACY_HOOK_COMMANDS = {'python3 "$(git rev-parse --show-toplevel)/.bezalel/base/scripts/project.py" '
                        'update --project "$(git rev-parse --show-toplevel)" --hook'}


def location(root, name):
    """O último componente pode ser um link gerenciado; pais nunca podem ser links."""
    path = Path(name)
    inside(root, path.parent.as_posix()) if len(path.parts) > 1 else None
    if path.is_absolute() or '..' in path.parts:
        raise DistributionError('Destino fora do projeto.')
    return Path(root) / path


def current(path):
    if path.is_symlink():
        return {'kind': 'link', 'target': os.readlink(path)}
    if path.is_file():
        return {'kind': 'file', 'sha256': digest(path.read_bytes())}
    if path.exists():
        raise DistributionError('Destino existente não é um arquivo gerenciável: ' + str(path))
    return None


def main_checkout(path):
    first = git(path, 'worktree', 'list', '--porcelain').decode().splitlines()[:1]
    if not first or not first[0].startswith('worktree '):
        raise DistributionError('Checkout principal do projeto não identificado.')
    return Path(first[0][len('worktree '):]).resolve()


def link_worktree(project, worktree):
    """Aponta .bezalel/base da worktree para a base do checkout principal, sem cópia."""
    if worktree == project:
        return False
    base = inside(project, '.bezalel/base')
    link = inside(worktree, '.bezalel') / 'base'
    if link.is_symlink() and Path(os.readlink(link)) == base:
        return False
    if link.is_symlink() or link.exists():
        raise DistributionError('A worktree já tem .bezalel/base próprio; reconcilie manualmente: ' + str(worktree))
    try:
        git(worktree, 'check-ignore', '-q', '--no-index', '.bezalel/base')
    except DistributionError as error:
        raise DistributionError('Ignore /base em .bezalel/.gitignore da worktree antes de ligá-la.') from error
    link.parent.mkdir(parents=True, exist_ok=True)
    link.symlink_to(base, target_is_directory=True)
    return True


def manual_skill(path):
    metadata = path / 'agents/openai.yaml'
    return metadata.is_file() and bool(re.search(r'allow_implicit_invocation:\s*false\b', metadata.read_text()))


def desired(project, base, platforms, automatic, contract_dir='agents'):
    # Grok Build descobre os adaptadores Claude; mantenha uma única cópia gerenciada.
    platforms = list(dict.fromkeys('claude' if name == 'grok' else name for name in platforms))
    contract_root = (base / contract_dir).resolve()
    catalog = read_json(base / contract_dir / 'catalog.json')
    if catalog.get('schema_version') != 3 or len(catalog.get('roles', {})) != 9:
        raise DistributionError('Catálogo de agentes incompatível.')
    entries = {}
    for path in sorted((base / 'skills').iterdir()):
        if path.is_symlink():
            raise DistributionError('Skill de origem não pode ser um link.')
        if not (path / 'SKILL.md').is_file():
            continue
        name = path.name
        if not re.fullmatch('[a-z0-9-]+', name):
            raise DistributionError('Nome de skill inválido.')
        if 'codex' in platforms:
            entries['.agents/skills/' + name] = {'kind': 'link', 'target': '../../.bezalel/base/skills/' + name}
        if 'claude' in platforms:
            if manual_skill(path):
                # Um comando explícito referencia o original, sem adaptar seu SKILL.md.
                entries['.claude/commands/bezalel-' + name + '.md'] = {
                    'kind': 'file', 'content': '\n'.join([
                        '---', 'description: "Executar ' + name + ' quando solicitado explicitamente"',
                        'disable-model-invocation: true', '---', '',
                        'Leia `.bezalel/base/skills/' + name + '/SKILL.md` na raiz do projeto.',
                        'Use essa pasta como origem de scripts e referências. Respeite as instruções',
                        'do projeto e o escopo autorizado. Disponibilidade não autoriza ações externas.', '',
                    ])}
            else:
                entries['.claude/skills/' + name] = {'kind': 'link', 'target': '../../.bezalel/base/skills/' + name}
    for role, entry in catalog['roles'].items():
        if not re.fullmatch('[a-z0-9-]+', role):
            raise DistributionError('Nome de agente inválido.')
        for platform in platforms:
            adapter = inside(contract_root, entry[platform])
            suffix = '.toml' if platform == 'codex' else '.md'
            if (adapter.parent != contract_root / platform or adapter.suffix != suffix
                    or not re.fullmatch('[a-z0-9-]+', adapter.stem)):
                raise DistributionError('Caminho de adaptador inválido no catálogo.')
            target = '.' + platform + '/agents/' + adapter.name
            if target in entries:
                raise DistributionError('Adaptador duplicado no catálogo.')
            entries[target] = {
                'kind': 'file', 'content': adapter.read_text()}
    instructions = '\n'.join([
        '## Uso do Bezalel neste projeto', '',
        '- Bezalel é o plugin; DreamTeam é a equipe de agentes de desenvolvimento.',
        '- Leia `.bezalel/project.json` e seus documentos de arquitetura e negócio.',
        '- Use o contrato do papel atribuído, as regras comuns de',
        '  `.bezalel/base/agents/' + catalog['workflow']['source'] + '` e somente os processos do papel',
        '  em `.bezalel/base/agents/processes/`; selecione skills pela relação',
        '  `.bezalel/base/agents/' + catalog['workflow']['skills'] + '`.',
        '- Quem inicia a conversa indica o modelo apropriado para a demanda e cada atribuição.',
        '  Ao delegar, siga `.bezalel/base/agents/coordenacao.md`: priorize modelos menores que o inicial,',
        '  selecione explicitamente quando suportado e justifique exceções no handoff.',
        '  Sem suporte, informe a limitação; não alegue troca de modelo executada.',
        '- Atribua trabalho aos agentes pertinentes quando a tarefa autorizar delegação.',
        '  TL coordena/revisa; um dev integra; QA e AppSec verificam independentemente.',
        '  Aprovação humana não pode ser simulada. Merge e deploy são manuais.',
        '- O fluxo é local. Banco exige HTML revisável; após decisão final registrada,',
        '  exclua a cópia temporária, preservando resumo e decisão fora dela.',
        '- Ao concluir desenvolvimento/validações técnicas, abra a PR com roteiro, pronta para revisão e sem draft,',
        '  salvo restrição expressa; aceite humano vem na PR. Após aprovação ou aviso',
        '  humano, confirme merge no serviço antes de fechar issues e executar env destroy',
        '  no ambiente associado à branch da tarefa, com preservação e limites da skill.',
        '- Para novas branches/worktrees, use uma descrição curta separada por hífens,',
        '  em minúsculas e sem acentos; números só quando significativos. Sem prefixos',
        '  de agente/tipo (codex/, feat/) ou sufixos aleatórios. Branch, pasta e nome',
        '  do ambiente ENV devem coincidir. Preserve nomes/vínculos preexistentes.',
        '- Scripts e referências partem da pasta real da skill carregada.',
        '- Ao mudar comandos, estrutura ou regras do projeto, atualize seu README e',
        '  AGENTS.md/CLAUDE.md. Preserve as instruções próprias fora deste bloco.',
        '- Esta instalação não concede acesso nem inicia o fluxo da DreamTeam automaticamente.',
    ])
    instructions = instructions.replace('.bezalel/base/agents/', '.bezalel/base/' + contract_dir + '/')
    for name in ['AGENTS.md', *(['CLAUDE.md'] if 'claude' in platforms else [])]:
        entries[name] = {'kind': 'block', 'content': instructions}
    entries['README.md'] = {'kind': 'block', 'content': '\n'.join([
        '## Bezalel neste projeto', '',
        'Agentes, skills e processo: `.bezalel/base/README.md`.',
        'Contexto próprio: `.bezalel/project.json` (preencher antes do primeiro trabalho).',
        'Atualizar: `python3 .bezalel/base/scripts/project.py update --project .`.',
        'Consultar revisão e integridade: `python3 .bezalel/base/scripts/project.py status --project .`.',
        'Desligar: `python3 .bezalel/base/scripts/project.py disable --project .`.',
        'Atualização automática no início de sessão: ' + ('ligada.' if automatic else 'desligada.'),
    ])}
    if automatic:
        hook = {'matcher': 'startup', 'hooks': [{'type': 'command', 'command': HOOK_COMMAND, 'timeout': 60}]}
        for platform in platforms:
            name = '.codex/hooks.json' if platform == 'codex' else '.claude/settings.local.json'
            entries[name] = {'kind': 'hook', 'entry': hook}
    return entries


def bezalel_hook(hook, previous=None):
    commands = {HOOK_COMMAND, *LEGACY_HOOK_COMMANDS}
    if previous:
        commands.update(item.get('command') for item in previous['entry'].get('hooks', []))
    items = hook.get('hooks', []) if isinstance(hook, dict) else []
    return any(isinstance(item, dict) and item.get('command') in commands for item in items)


def extract_block(content):
    if content.count(START) != 1 or content.count(END) != 1:
        raise DistributionError('Bloco Bezalel ausente ou ambíguo; preserve e reconcilie as instruções.')
    start, end = content.index(START), content.index(END) + len(END)
    if start >= content.index(END):
        raise DistributionError('Marcadores Bezalel invertidos.')
    return content[start:end]


def plan(project, old, entries):
    changes, managed = {}, {}
    for name in sorted(old.keys() | entries.keys()):
        path = location(project, name)
        previous, entry = old.get(name), entries.get(name)
        kind = (entry or previous)['kind']
        actual = current(path)
        if kind in {'file', 'link'}:
            # Ausência não é customização: recria-se ou apenas sai do registro.
            if actual != previous and not (previous and actual is None):
                raise DistributionError('Destino personalizado ou não gerenciado: ' + name)
            if entry is None:
                if actual is not None:
                    changes[name] = None
            elif kind == 'link':
                managed[name] = entry
                if entry != actual:
                    changes[name] = entry
            else:
                managed[name] = {'kind': 'file', 'sha256': digest(entry['content'].encode())}
                if managed[name] != actual:
                    changes[name] = entry
        elif kind == 'block':
            if path.is_symlink():
                raise DistributionError('Instrução do projeto não pode ser um link: ' + name)
            content = path.read_text() if actual else ''
            if previous and START not in content and END not in content:
                previous = None
            if not previous and not entry:
                continue
            existing = extract_block(content) if previous else ''
            if previous and digest(existing.encode()) != previous['sha256']:
                raise DistributionError('Bloco de instruções personalizado: ' + name)
            if not previous and (START in content or END in content):
                raise DistributionError('Bloco existente sem registro: ' + name)
            block = START + '\n' + entry['content'] + '\n' + END if entry else ''
            result = content.replace(existing, block, 1) if previous else content + ('\n\n' if content else '') + block + '\n'
            if result != content:
                changes[name] = {'kind': 'file', 'content': result}
            if entry:
                managed[name] = {'kind': 'block', 'sha256': digest(block.encode())}
        elif kind == 'hook':
            if path.is_symlink():
                raise DistributionError('Configuração não pode ser um link: ' + name)
            config = read_json(path) if actual else {}
            hooks = config.setdefault('hooks', {}).setdefault('SessionStart', [])
            count = hooks.count(previous['entry']) if previous else 0
            if count > 1:
                raise DistributionError('Hook Bezalel duplicado: ' + name)
            if count:
                hooks.remove(previous['entry'])
            elif any(bezalel_hook(hook, previous) for hook in hooks):
                raise DistributionError(('Hook Bezalel personalizado: ' if previous else
                                         'Hook Bezalel existente sem registro: ') + name)
            if entry:
                hooks.append(entry['entry'])
                managed[name] = entry
            if not actual and not entry:
                continue
            result = json_bytes(config).decode()
            if not actual or path.read_text() != result:
                changes[name] = {'kind': 'file', 'content': result}
        else:
            raise DistributionError('Tipo de instalação não suportado.')
        if name in changes:
            changes[name] = {**(changes[name] or {'kind': 'remove'}), 'expected': actual}
    return changes, managed


def apply(project, changes):
    """Não substitui diretórios; reverte os arquivos desta operação em erro normal."""
    backups = {}
    try:
        for name, entry in changes.items():
            path = location(project, name)
            kind = current(path)
            if entry is not None and 'expected' in entry and kind != entry['expected']:
                raise DistributionError('Arquivo mudou durante a atualização: ' + name)
            backups[name] = ('link', os.readlink(path)) if kind and kind['kind'] == 'link' else (
                ('file', path.read_bytes(), path.stat().st_mode & 0o777) if kind else None)
            if entry and entry['kind'] == 'file':
                atomic_write(path, entry['content'].encode(), backups[name][2] if backups[name] and backups[name][0] == 'file' else 0o644)
            else:
                if kind:
                    path.unlink()
                if entry and entry['kind'] == 'link':
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.symlink_to(entry['target'])
    except BaseException:
        for name, backup in reversed(list(backups.items())):
            path = location(project, name)
            if path.is_file() or path.is_symlink():
                path.unlink()
            if backup and backup[0] == 'link':
                path.symlink_to(backup[1])
            elif backup:
                atomic_write(path, backup[1], backup[2])
        raise


def reconcile(project, base, state, platforms, automatic, revision, disable=False, extra=None):
    entries = {} if disable else desired(project, base, platforms, automatic)
    changes, managed = plan(project, state.get('managed', {}), entries)
    changes.update(extra or {})
    new = {'schema_version': 1, 'enabled': not disable, 'platforms': platforms,
           'automatic': automatic, 'branch': state.get('branch', 'master'),
           'revision': revision, 'managed': managed}
    changes[STATE] = {'kind': 'file', 'content': json_bytes(new).decode()}
    apply(project, changes)
    return new


def snapshot(repo, revision, target):
    archive = git(repo, 'archive', '--format=tar', revision)
    with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
        for member in stream.getmembers():
            if member.isdir():
                continue
            if not member.isfile():
                raise DistributionError('Revisão contém links ou arquivos especiais.')
            path = inside(target, member.name)
            atomic_write(path, stream.extractfile(member).read(), member.mode & 0o777)


def update(project, state):
    if not state.get('enabled'):
        return False
    base = inside(project, '.bezalel/base')
    if git(base, 'status', '--porcelain').strip():
        raise DistributionError('Base Bezalel tem mudanças locais; atualização preservada e bloqueada.')
    previous = git(base, 'rev-parse', 'HEAD').decode().strip()
    if previous != state['revision']:
        raise DistributionError('Base foi trocada fora do atualizador; reconcilie a revisão explicitamente.')
    branch = state['branch']
    git(base, 'check-ref-format', '--branch', branch)
    git(base, 'fetch', '--quiet', '--no-tags', 'origin', 'refs/heads/' + branch, timeout=25)
    revision = git(base, 'rev-parse', 'FETCH_HEAD^{commit}').decode().strip()
    git(base, 'merge-base', '--is-ancestor', previous, revision)
    with tempfile.TemporaryDirectory(prefix='bezalel-candidate-') as temporary:
        candidate = Path(temporary).resolve()
        snapshot(base, revision, candidate)
        # Valida a nova árvore com o checker já adotado; não executa scripts novos.
        import check_repository
        original_root = check_repository.ROOT
        try:
            check_repository.ROOT = candidate
            errors = (check_repository.validate_structure(check_repository.package_files())
                      + check_repository.validate_agents() + check_repository.validate_upstream()
                      + check_repository.validate_workbook_template())
        finally:
            check_repository.ROOT = original_root
        if errors:
            raise DistributionError('Nova revisão não passou na validação estrutural: ' + '; '.join(errors[:3]))
        entries = desired(project, candidate, state['platforms'], state['automatic'])
        plan(project, state['managed'], entries)
        try:
            if revision != previous:
                git(base, 'checkout', '--quiet', '--detach', revision)
            reconcile(project, candidate, state, state['platforms'], state['automatic'], revision)
        except BaseException:
            if revision != previous:
                git(base, 'checkout', '--quiet', '--detach', previous)
            raise
    return revision != previous


@contextlib.contextmanager
def lock(project):
    path = inside(project, '.bezalel/update.lock')
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a') as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise DistributionError('Outra atualização do Bezalel está em andamento.') from error
        yield


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['enable', 'update', 'status', 'disable', 'run', 'link-worktree'])
    parser.add_argument('--project', type=Path, default=Path.cwd())
    parser.add_argument('--platform', choices=['both', 'codex', 'claude', 'grok'], default='both')
    parser.add_argument('--branch', default='master')
    parser.add_argument('--no-auto-update', action='store_true')
    parser.add_argument('--hook', action='store_true')
    parser.add_argument('--app', choices=['codex', 'claude', 'grok'])
    args = parser.parse_args()
    try:
        project = args.project.resolve()
        if Path(git(project, 'rev-parse', '--show-toplevel').decode().strip()).resolve() != project:
            raise DistributionError('Use a raiz do projeto Git.')
        if args.action == 'link-worktree':
            worktree, project = project, main_checkout(project)
            if worktree == project:
                raise DistributionError('Informe a raiz de uma worktree, não o checkout principal.')
            state_path = inside(project, STATE)
            if not (state_path.is_file() and read_json(state_path).get('enabled')):
                raise DistributionError('Bezalel não está ligado no checkout principal.')
            linked = link_worktree(project, worktree)
            print('Worktree ligada à base do checkout principal.' if linked else 'Worktree já estava ligada.')
            return 0
        state_path = inside(project, STATE)
        with lock(project):
            state = read_json(state_path) if state_path.is_file() else {}
            if state and state.get('schema_version') != 1:
                raise DistributionError('Registro de instalação incompatível.')
            if args.action == 'enable':
                base = inside(project, '.bezalel/base')
                if not (base / 'agents/catalog.json').is_file():
                    raise DistributionError('Clone uma versão publicada em .bezalel/base antes de ligar.')
                if Path(git(base, 'rev-parse', '--show-toplevel').decode().strip()).resolve() != base:
                    raise DistributionError('A base deve ser um clone Git próprio.')
                git(base, 'check-ref-format', '--branch', args.branch)
                platforms = ['codex', 'claude'] if args.platform == 'both' else [args.platform]
                revision = git(base, 'rev-parse', 'HEAD').decode().strip()
                # Sem sobrescrever contexto: copie o exemplo somente na primeira adoção.
                context = inside(project, '.bezalel/project.json')
                entries = desired(project, base, platforms, not args.no_auto_update)
                plan(project, state.get('managed', {}), entries)
                state['branch'] = args.branch
                extra = {}
                if not context.exists():
                    extra['.bezalel/project.json'] = {'kind': 'file', 'content': (base / '.bezalel/project.example.json').read_text()}
                ignore = inside(project, '.bezalel/.gitignore')
                rules = ignore.read_text() if ignore.exists() else ''
                # '/base' também ignora o link criado em worktrees; '/base/' só ignora diretórios.
                additions = [p for p in ['/base', '/install.local.json', '/update.lock', '/vps-deploy.local.json', '/deliveries/*.local.json', '/reviews/'] if p not in rules.splitlines()]
                if additions:
                    extra['.bezalel/.gitignore'] = {'kind': 'file', 'content': rules.rstrip('\n') + '\n' + '\n'.join(additions) + '\n'}
                reconcile(project, base, state, platforms, not args.no_auto_update, revision, extra=extra)
                message = 'Bezalel ligado. Preencha .bezalel/project.json e confira a descoberta em uma nova sessão.'
            elif args.action == 'status':
                if state.get('enabled'):
                    entries = desired(project, project / '.bezalel/base', state['platforms'], state['automatic'])
                    changes, _ = plan(project, state['managed'], entries)
                    if changes:
                        raise DistributionError('Instalação requer reconciliação; há arquivos divergentes.')
                    state['local_changes'] = bool(git(project / '.bezalel/base', 'status', '--porcelain').strip())
                    state['actual_revision'] = git(project / '.bezalel/base', 'rev-parse', 'HEAD').decode().strip()
                message = json_bytes({k: v for k, v in state.items() if k != 'managed'}).decode().strip() or 'Não instalado.'
            elif args.action == 'disable':
                if state:
                    reconcile(project, project / '.bezalel/base', state, state['platforms'], False, state['revision'], disable=True)
                message = 'Integração desligada; contexto próprio e base preservados.'
            else:
                if not state.get('enabled'):
                    raise DistributionError('Bezalel não está ligado neste projeto.')
                if args.hook and not state.get('automatic'):
                    return 0
                changed = update(project, state)
                message = ('Bezalel atualizado. Reabra a sessão para carregar todos os agentes e skills novos.'
                           if changed else 'Bezalel já está atualizado.')
                if args.hook:
                    # O hook roda na sessão; uma worktree do projeto recebe o link para a base.
                    here = Path(git(Path.cwd(), 'rev-parse', '--show-toplevel').decode().strip()).resolve()
                    if here != project and main_checkout(here) == project and link_worktree(project, here):
                        message = (message if changed else '') + (' ' if changed else '') + (
                            'Worktree ligada à base do Bezalel. Reabra a sessão para carregar agentes e skills.')
                        changed = True
        if args.action == 'run':
            app = args.app
            if not app or not shutil.which(app):
                raise DistributionError('Informe --app codex, --app claude ou --app grok e instale o aplicativo previamente.')
            return subprocess.call([app], cwd=project)
        if args.hook:
            if changed:
                print(json_bytes({'hookSpecificOutput': {'hookEventName': 'SessionStart', 'additionalContext': message}}).decode(), end='')
        else:
            print(message)
        return 0
    except (DistributionError, OSError, ValueError, KeyError, TypeError) as error:
        print('Bezalel: ' + (str(error) if isinstance(error, DistributionError) else 'instalação/configuração inválida; operação não concluída.'), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
