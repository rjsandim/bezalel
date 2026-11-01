#!/usr/bin/env python3
"""Liga, atualiza ou desliga o Bezalel por projeto, preservando customizações."""
import argparse
import contextlib
import copy
import fcntl
import io
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tarfile
import tempfile
import threading

from distribution import (DistributionError, atomic_write, digest, git, inside,
                          json_bytes, newline, read_json, read_text)

ROOT = Path(__file__).resolve().parents[1]
STATE = '.bezalel/install.local.json'
START, END = '<!-- bezalel:begin -->', '<!-- bezalel:end -->'
# A base fica no checkout principal; em worktrees o hook a atualiza e liga a worktree atual.
HOOK_COMMAND = ('r="$(git worktree list --porcelain | sed -n \'1s/^worktree //p\')"; '
                's="$r/.bezalel/base/scripts/project.py"; '
                '[ ! -f "$s" ] || python3 "$s" update --project "$r" --hook')
LEGACY_HOOK_COMMANDS = {'python3 "$(git rev-parse --show-toplevel)/.bezalel/base/scripts/project.py" '
                        'update --project "$(git rev-parse --show-toplevel)" --hook'}


class Interrupted(DistributionError):
    pass


@contextlib.contextmanager
def shielded():
    """Adia SIGTERM durante checkout e reversões; o sinal pendente é entregue ao final."""
    previous = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGTERM})
    try:
        yield
    finally:
        signal.pthread_sigmask(signal.SIG_SETMASK, previous)


@contextlib.contextmanager
def terminable():
    """SIGTERM (por exemplo, o prazo do hook) vira exceção uma vez e aciona a reversão normal."""
    if threading.current_thread() is not threading.main_thread():
        yield
        return
    armed = True

    def handler(signum, frame):
        nonlocal armed
        if armed:
            armed = False
            raise Interrupted('Atualização interrompida por sinal; a revisão anterior foi preservada.')
    previous = signal.signal(signal.SIGTERM, handler)
    try:
        yield
    finally:
        signal.signal(signal.SIGTERM, previous)


def append_lines(text, lines):
    """Acrescenta linhas no final de linha predominante do arquivo."""
    nl = newline(text)
    return text.rstrip('\r\n') + nl + nl.join(lines) + nl


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
    return metadata.is_file() and bool(re.search(r'allow_implicit_invocation:\s*false\b', read_text(metadata)))


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
                'kind': 'file', 'content': read_text(adapter)}
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


def block_span(content):
    if content.count(START) != 1 or content.count(END) != 1:
        raise DistributionError('Bloco Bezalel ausente ou ambíguo; preserve e reconcilie as instruções.')
    start, end = content.index(START), content.index(END) + len(END)
    if start >= content.index(END):
        raise DistributionError('Marcadores Bezalel invertidos.')
    return start, end


def plan_entry(project, name, previous, entry):
    """Mudança de um destino: (mudança ou None, registro gerenciado ou None)."""
    path = location(project, name)
    kind = (entry or previous)['kind']
    actual = current(path)
    change = record = None
    if kind in {'file', 'link'}:
        # Ausência não é customização: recria-se ou apenas sai do registro.
        if actual != previous and not (previous and actual is None):
            raise DistributionError('Destino personalizado ou não gerenciado: ' + name)
        if entry is None:
            if actual is not None:
                change = {'kind': 'remove'}
        elif kind == 'link':
            record = entry
            if entry != actual:
                change = entry
        else:
            record = {'kind': 'file', 'sha256': digest(entry['content'].encode('utf-8'))}
            if record != actual:
                change = entry
    elif kind == 'block':
        if path.is_symlink():
            raise DistributionError('Instrução do projeto não pode ser um link: ' + name)
        content = read_text(path) if actual else ''
        nl = newline(content)
        if previous and START not in content and END not in content:
            previous = None
        if not previous and not entry:
            return None, None
        if previous:
            start, end = block_span(content)
            # O registro guarda o bloco em LF; o arquivo mantém seu final de linha.
            if digest(content[start:end].replace('\r\n', '\n').encode('utf-8')) != previous['sha256']:
                raise DistributionError('Bloco de instruções personalizado: ' + name)
        elif START in content or END in content:
            raise DistributionError('Bloco existente sem registro: ' + name)
        block = START + '\n' + entry['content'] + '\n' + END if entry else ''
        if previous and entry:
            result = content[:start] + block.replace('\n', nl) + content[end:]
            layout = {key: previous[key] for key in ('before', 'after', 'created') if key in previous}
        elif previous:
            # Remove também o separador acrescentado na inclusão; registros antigos usavam '\n\n' e '\n'.
            before = previous.get('before', '\n\n' if start else '').replace('\n', nl)
            after = previous.get('after', '\n').replace('\n', nl)
            if start >= len(before) and content[start - len(before):start] == before:
                start -= len(before)
            if content[end:end + len(after)] == after:
                end += len(after)
            result = content[:start] + content[end:]
        else:
            before = (nl if content and not content.endswith(nl) else '') + (nl if content else '')
            result = content + before + block.replace('\n', nl) + nl
            layout = {'before': before.replace('\r\n', '\n'), 'after': '\n', 'created': actual is None}
        if entry:
            record = {'kind': 'block', 'sha256': digest(block.encode('utf-8')), **layout}
        if result != content:
            # Arquivo criado pelo enable e esvaziado pelo disable volta a não existir.
            change = ({'kind': 'remove'} if not entry and not result and previous.get('created')
                      else {'kind': 'file', 'content': result})
    elif kind == 'hook':
        if path.is_symlink():
            raise DistributionError('Configuração não pode ser um link: ' + name)
        config = read_json(path) if actual else {}
        section = config.get('hooks', {}) if isinstance(config, dict) else None
        if not isinstance(section, dict) or not isinstance(section.get('SessionStart', []), list):
            raise DistributionError('Configuração de hooks inválida: ' + name)
        original = copy.deepcopy(config)
        hooks = section.get('SessionStart', [])
        # Contêineres criados pelo instalador saem no disable quando vazios; os do usuário ficam.
        created = previous.get('created', []) if previous and actual else [
            part for part, missing in [('file', not actual), ('hooks', 'hooks' not in config),
                                       ('SessionStart', 'SessionStart' not in section)] if missing]
        count = hooks.count(previous['entry']) if previous else 0
        if count > 1:
            raise DistributionError('Hook Bezalel duplicado: ' + name)
        if not count and any(bezalel_hook(hook, previous) for hook in hooks):
            raise DistributionError(('Hook Bezalel personalizado: ' if previous else
                                     'Hook Bezalel existente sem registro: ') + name)
        if entry:
            hooks = config.setdefault('hooks', {}).setdefault('SessionStart', [])
            if count:
                hooks[hooks.index(previous['entry'])] = entry['entry']
            else:
                hooks.append(entry['entry'])
            record = {**entry, 'created': created}
        elif count:
            hooks.remove(previous['entry'])
            if 'SessionStart' in created and not hooks:
                del section['SessionStart']
            if 'hooks' in created and not section:
                del config['hooks']
        # Compara o conteúdo, não a formatação: reformatar o arquivo não é divergência.
        if config != original:
            change = ({'kind': 'remove'} if not entry and 'file' in created and not config
                      else {'kind': 'file', 'content': json_bytes(config).decode('utf-8')})
    else:
        raise DistributionError('Tipo de instalação não suportado.')
    return ({**change, 'expected': actual} if change else None), record


def plan(project, old, entries, alternatives=None):
    """`alternatives` traz o registro gravado antes de uma atualização interrompida."""
    changes, managed = {}, {}
    for name in sorted(old.keys() | entries.keys()):
        previous, entry = old.get(name), entries.get(name)
        try:
            change, record = plan_entry(project, name, previous, entry)
        except DistributionError:
            other = (alternatives or {}).get(name)
            if other is None or other == previous:
                raise
            # Gravação parcial: o destino já corresponde ao registro da atualização pendente.
            change, record = plan_entry(project, name, other, entry)
        if change:
            changes[name] = change
        if record:
            managed[name] = record
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
                atomic_write(path, entry['content'].encode('utf-8'), backups[name][2] if backups[name] and backups[name][0] == 'file' else 0o644)
            else:
                if kind:
                    path.unlink()
                if entry and entry['kind'] == 'link':
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.symlink_to(entry['target'])
    except BaseException:
        with shielded():
            for name, backup in reversed(list(backups.items())):
                path = location(project, name)
                if path.is_file() or path.is_symlink():
                    path.unlink()
                if backup and backup[0] == 'link':
                    path.symlink_to(backup[1])
                elif backup:
                    atomic_write(path, backup[1], backup[2])
        raise


def reconcile(project, base, state, platforms, automatic, revision, disable=False, extra=None, alternatives=None):
    entries = {} if disable else desired(project, base, platforms, automatic)
    changes, managed = plan(project, state.get('managed', {}), entries, alternatives)
    changes.update(extra or {})
    new = {'schema_version': 1, 'enabled': not disable, 'platforms': platforms,
           'automatic': automatic, 'branch': state.get('branch', 'master'),
           'revision': revision, 'managed': managed}
    changes[STATE] = {'kind': 'file', 'content': json_bytes(new).decode('utf-8')}
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


def resume(project, base, state):
    """Conclui uma atualização interrompida (ex.: SIGKILL) sem força nem reset.

    O marcador é gravado após validar o destino e antes do checkout. Com HEAD na
    origem ou no destino, reconcilia os arquivos com a base atual aceitando, por
    destino, o registro anterior ou o planejado; outra revisão exige ação manual.
    """
    pending = state['pending']
    clean = {key: value for key, value in state.items() if key != 'pending'}
    if (not isinstance(pending, dict) or not {'from', 'to', 'managed'} <= pending.keys()
            or pending['from'] != clean.get('revision')):
        raise DistributionError('Marcador de atualização pendente inválido; reconcilie a instalação explicitamente.')
    if git(base, 'status', '--porcelain').strip():
        raise DistributionError('Atualização interrompida deixou mudanças na base; preserve-as e reconcilie manualmente.')
    head = git(base, 'rev-parse', 'HEAD').decode().strip()
    if head not in (pending['from'], pending['to']):
        raise DistributionError('Base fora das revisões da atualização interrompida; reconcilie a revisão explicitamente.')
    if head != pending['from']:
        git(base, 'merge-base', '--is-ancestor', pending['from'], head)
    new = reconcile(project, base, clean, clean['platforms'], clean['automatic'], head,
                    alternatives=pending['managed'])
    return new, head != pending['from']


def update(project, state):
    if not state.get('enabled'):
        return False
    base = inside(project, '.bezalel/base')
    state_path = inside(project, STATE)
    with terminable():
        resumed = False
        if state.get('pending'):
            state, resumed = resume(project, base, state)
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
            _, managed = plan(project, state['managed'], entries)
            # Marcador antes do checkout: um processo morto entre checkout e registro é retomado.
            marked = {**state, 'pending': {'from': previous, 'to': revision, 'managed': managed}}
            written = False
            try:
                atomic_write(state_path, json_bytes(marked))
                written = True
                if revision != previous:
                    with shielded():
                        git(base, 'checkout', '--quiet', '--detach', revision)
                reconcile(project, candidate, state, state['platforms'], state['automatic'], revision)
            except BaseException as error:
                with shielded():
                    # Sem marcador confirmado nada foi trocado (um marcador gravado é retomado depois).
                    # Registro final sem marcador: o sinal chegou após a conclusão; não reverta.
                    if not written:
                        raise
                    if 'pending' not in read_json(state_path):
                        if not isinstance(error, Interrupted):
                            raise
                    else:
                        if revision != previous:
                            git(base, 'checkout', '--quiet', '--detach', previous)
                        atomic_write(state_path, json_bytes(state))
                        raise
    return resumed or revision != previous


@contextlib.contextmanager
def lock(project):
    path = inside(project, '.bezalel/update.lock')
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('ab') as stream:
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
            if state.get('pending') and args.action in {'enable', 'status', 'disable'}:
                raise DistributionError('Há uma atualização interrompida; execute update para concluí-la primeiro.')
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
                    extra['.bezalel/project.json'] = {'kind': 'file', 'content': read_text(base / '.bezalel/project.example.json')}
                ignore = inside(project, '.bezalel/.gitignore')
                rules = read_text(ignore) if ignore.exists() else ''
                # '/base' também ignora o link criado em worktrees; '/base/' só ignora diretórios.
                additions = [p for p in ['/base', '/install.local.json', '/update.lock', '/vps-deploy.local.json', '/deliveries/*.local.json', '/reviews/'] if p not in rules.splitlines()]
                if additions:
                    extra['.bezalel/.gitignore'] = {'kind': 'file', 'content': append_lines(rules, additions)}
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
                message = json_bytes({k: v for k, v in state.items() if k != 'managed'}).decode('utf-8').strip() or 'Não instalado.'
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
