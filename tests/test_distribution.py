"""Distribuição em repositórios sintéticos; não instala plugins ou chama serviços."""
import ast
import contextlib
import copy
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import distribution as dist
import plugin
import project
import sync_upstream
import check_repository


def commit(root, message='Fixture'):
    dist.git(root, 'add', '-A')
    dist.git(root, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', message)
    return dist.git(root, 'rev-parse', 'HEAD').decode().strip()


def init(root):
    root.mkdir(parents=True, exist_ok=True)
    dist.git(root, 'init', '-q', '-b', 'master')


# Processo filho que morre (SIGKILL) ou recebe SIGTERM num ponto exato do update.
INTERRUPTED_UPDATE = '''
import os, signal, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import distribution, project
consumer, target, mode = Path(sys.argv[2]), sys.argv[3], sys.argv[4]
real_write, real_git = project.atomic_write, project.git
def stop():
    os.kill(os.getpid(), signal.SIGKILL if mode == "kill" else signal.SIGTERM)
def write(path, data, permissions=0o644):
    if Path(path).as_posix().endswith(target) and b'"pending"' not in data:
        stop()
    return real_write(path, data, permissions)
def git(root, *args, **kwargs):
    if target == "checkout" and args[:1] == ("checkout",):
        stop()
    return real_git(root, *args, **kwargs)
project.atomic_write, project.git = write, git
try:
    project.update(consumer, distribution.read_json(consumer / project.STATE))
except distribution.DistributionError as error:
    print(error, file=sys.stderr)
    sys.exit(3)
'''


def rename_agent(source, role, name):
    catalog_path = source / 'agents/catalog.json'
    catalog = dist.read_json(catalog_path)
    previous = dict(catalog['roles'][role])
    for platform in ['codex', 'claude']:
        old = source / 'agents' / previous[platform]
        new = old.with_name(name + old.suffix)
        new.write_text(old.read_text().replace(old.stem, name))
        old.unlink()
        catalog['roles'][role][platform] = new.relative_to(source / 'agents').as_posix()
    catalog_path.write_bytes(dist.json_bytes(catalog))
    return previous


class DistributionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='bezalel fixture ')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def consumer(self):
        consumer = self.root / 'projeto com espaços'
        init(consumer)
        (consumer / 'README.md').write_text('Conteúdo próprio.\n')
        (consumer / 'AGENTS.md').write_text('Regras do projeto.\n')
        return consumer

    def source(self):
        source = self.root / 'source'
        init(source)
        for folder in ['agents', 'skills', 'scripts', 'tests', '.bezalel', '.github']:
            shutil.copytree(ROOT / folder, source / folder,
                            ignore=shutil.ignore_patterns('.DS_Store', '__pycache__', 'state', 'backups'))
        for name in ['README.md', 'AGENTS.md', '.gitignore']:
            shutil.copy2(ROOT / name, source / name)
        commit(source)
        return source

    def connected(self):
        source, consumer = self.source(), self.consumer()
        base = consumer / '.bezalel/base'
        dist.git(consumer, 'clone', '-q', '--', str(source), str(base))
        revision = dist.git(base, 'rev-parse', 'HEAD').decode().strip()
        state = project.reconcile(consumer, base, {}, ['codex', 'claude'], True, revision)
        return source, consumer, base, state

    def test_install_supports_both_and_manual_commands_preserve_originals(self):
        consumer = self.consumer()
        before = (ROOT / 'skills/release/SKILL.md').read_bytes()
        state = project.reconcile(consumer, ROOT, {}, ['codex', 'claude'], True, 'fixture')
        self.assertTrue((consumer / '.agents/skills/release').is_symlink())
        self.assertFalse((consumer / '.claude/skills/release').exists())
        manual = (consumer / '.claude/commands/bezalel-release.md').read_text()
        self.assertIn('disable-model-invocation: true', manual)
        self.assertIn('.bezalel/base/skills/release/SKILL.md', manual)
        self.assertEqual((ROOT / 'skills/release/SKILL.md').read_bytes(), before)
        # ENV é implícita para o DevOps; as cinco manuais, VPS e limpeza seguem explícitas.
        self.assertTrue((consumer / '.claude/skills/env').is_symlink())
        self.assertFalse((consumer / '.claude/commands/bezalel-env.md').exists())
        commands = sorted(p.stem for p in (consumer / '.claude/commands').glob('bezalel-*.md'))
        self.assertEqual(commands, ['bezalel-' + name for name in sorted([
            'github-resolution', 'limpar-orbstack', 'pr-bump', 'pr-post-audit', 'reflect', 'release', 'vps-deploy'])])
        self.assertEqual(len(list((consumer / '.codex/agents').glob('*.toml'))), 9)
        self.assertEqual(len(list((consumer / '.claude/agents').glob('*.md'))), 9)
        for adapter in [*(consumer / '.codex/agents').glob('*.toml'), *(consumer / '.claude/agents').glob('*.md')]:
            assigned = re.findall(r'agents/(processes/[A-Za-z]+\.md)', adapter.read_text())
            self.assertTrue(assigned and all((ROOT / 'agents' / name).is_file() for name in assigned))
        self.assertNotIn('agents/processes/plan.md', (consumer / '.codex/agents/dream-team-qa.toml').read_text())
        self.assertIn('.bezalel/base/agents/processes/', (consumer / 'AGENTS.md').read_text())
        self.assertTrue((consumer / 'AGENTS.md').read_text().startswith('Regras do projeto.'))
        self.assertIn('startup', json.dumps(state['managed']))

    def test_grok_reuses_claude_adapters_without_duplicate_agents(self):
        consumer = self.consumer()
        state = project.reconcile(consumer, ROOT, {}, ['grok'], False, 'fixture')
        self.assertEqual(state['platforms'], ['grok'])
        self.assertEqual(len(list((consumer / '.claude/agents').glob('*.md'))), 9)
        self.assertFalse((consumer / '.grok').exists())
        self.assertFalse((consumer / '.codex').exists())
        manual = (consumer / '.claude/commands/bezalel-release.md').read_text()
        self.assertIn('disable-model-invocation: true', manual)
        self.assertFalse((consumer / '.claude/skills/release').exists())
        self.assertEqual(project.desired(consumer, ROOT, ['grok', 'claude'], False),
                         project.desired(consumer, ROOT, ['claude'], False))
        migrated = project.reconcile(consumer, ROOT, state, ['claude'], False, 'fixture')
        project.reconcile(consumer, ROOT, migrated, ['grok'], False, 'fixture', disable=True)
        self.assertFalse((consumer / '.claude/agents/dream-team-qa.md').exists())
        self.assertEqual((consumer / 'AGENTS.md').read_text().strip(), 'Regras do projeto.')

    def test_grok_custom_adapter_blocks_update_and_disable(self):
        consumer = self.consumer()
        state = project.reconcile(consumer, ROOT, {}, ['grok'], False, 'fixture')
        adapter = consumer / '.claude/agents/dream-team-qa.md'
        adapter.write_text('Customizado')
        for disable in [False, True]:
            with self.subTest(disable=disable), self.assertRaises(dist.DistributionError):
                project.reconcile(consumer, ROOT, state, ['grok'], False, 'next', disable=disable)
        self.assertEqual(adapter.read_text(), 'Customizado')

    def test_grok_cli_lifecycle_and_new_skill_update(self):
        source, consumer = self.source(), self.consumer()
        base = consumer / '.bezalel/base'
        dist.git(consumer, 'clone', '-q', '--', str(source), str(base))
        def invoke(action):
            result = subprocess.run([sys.executable, '-B', str(base / 'scripts/project.py'), action,
                                     '--project', str(consumer), '--platform', 'grok', '--no-auto-update'],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        invoke('enable')
        invoke('status')
        self.assertFalse((consumer / '.claude/settings.local.json').exists())
        skill = source / 'skills/nova-skill'
        skill.mkdir()
        sections = ['Objetivo e escopo', 'Entradas e pré-requisitos', 'Procedimento',
                    'Saídas', 'Validação', 'Limites operacionais']
        (skill / 'SKILL.md').write_text('---\nname: nova-skill\ndescription: Nova skill\n---\n'
                                      + ''.join('## ' + section + '\nTexto.\n' for section in sections))
        commit(source, 'Nova skill')
        invoke('update')
        self.assertTrue((consumer / '.claude/skills/nova-skill/SKILL.md').is_file())
        invoke('status')
        invoke('disable')
        self.assertFalse((consumer / '.claude/agents/dream-team-qa.md').exists())

    def test_existing_agent_and_broken_link_are_not_adopted_or_overwritten(self):
        for kind in ['file', 'broken-link']:
            with self.subTest(kind=kind):
                consumer = self.root / kind
                path = consumer / '.codex/agents/dream-team-qa.toml'
                path.parent.mkdir(parents=True)
                if kind == 'file':
                    path.write_text('Customizado')
                else:
                    path.symlink_to('/missing')
                with self.assertRaises(dist.DistributionError):
                    project.reconcile(consumer, ROOT, {}, ['codex'], False, 'fixture')
                self.assertFalse((consumer / 'AGENTS.md').exists())
                self.assertTrue(path.is_symlink() if kind == 'broken-link' else path.read_text() == 'Customizado')

    def test_parent_symlink_cannot_write_outside_project(self):
        consumer = self.consumer()
        outside = self.root / 'outside'
        outside.mkdir()
        (consumer / '.codex').symlink_to(outside)
        with self.assertRaises(dist.DistributionError):
            project.reconcile(consumer, ROOT, {}, ['codex'], False, 'fixture')
        self.assertEqual(list(outside.iterdir()), [])

    def test_update_preserves_unrelated_documentation_and_hooks(self):
        consumer = self.consumer()
        hook_path = consumer / '.claude/settings.local.json'
        hook_path.parent.mkdir()
        unrelated = {'hooks': [{'type': 'command', 'command': 'fixture-command'}]}
        hook_path.write_text(json.dumps({'permissions': {'allow': ['Read']}, 'hooks': {'SessionStart': [unrelated]}}))
        state = project.reconcile(consumer, ROOT, {}, ['codex', 'claude'], True, 'fixture')
        with (consumer / 'AGENTS.md').open('a') as stream:
            stream.write('\nNova regra própria.\n')
        project.reconcile(consumer, ROOT, state, ['codex', 'claude'], True, 'fixture2')
        self.assertIn('Nova regra própria.', (consumer / 'AGENTS.md').read_text())
        config = dist.read_json(hook_path)
        self.assertEqual(config['permissions'], {'allow': ['Read']})
        self.assertIn(unrelated, config['hooks']['SessionStart'])
        self.assertEqual(len(config['hooks']['SessionStart']), 2)

    def test_custom_agent_and_managed_block_stop_update_before_any_writes(self):
        consumer = self.consumer()
        state = project.reconcile(consumer, ROOT, {}, ['codex'], False, 'fixture')
        path = consumer / '.codex/agents/dream-team-qa.toml'
        path.write_text('Minha customização')
        with self.assertRaises(dist.DistributionError):
            project.reconcile(consumer, ROOT, state, ['codex'], True, 'fixture2')
        self.assertFalse((consumer / '.codex/hooks.json').exists())
        self.assertEqual(dist.read_json(consumer / project.STATE)['revision'], 'fixture')

    def test_disable_preserves_project_context_and_unrelated_files(self):
        consumer = self.consumer()
        state = project.reconcile(consumer, ROOT, {}, ['codex', 'claude'], True, 'fixture')
        (consumer / '.bezalel/project.json').write_text('contexto próprio')
        project.reconcile(consumer, ROOT, state, ['codex', 'claude'], False, 'fixture', disable=True)
        self.assertFalse((consumer / '.codex/agents/dream-team-qa.toml').exists())
        self.assertFalse((consumer / '.agents/skills/release').is_symlink())
        self.assertNotIn(project.START, (consumer / 'AGENTS.md').read_text())
        self.assertIn('Regras do projeto.', (consumer / 'AGENTS.md').read_text())
        self.assertEqual((consumer / '.bezalel/project.json').read_text(), 'contexto próprio')

    def test_missing_managed_files_are_recreated_and_ignored_by_disable(self):
        consumer = self.consumer()
        state = project.reconcile(consumer, ROOT, {}, ['codex', 'claude'], True, 'fixture')
        missing = [consumer / '.codex/agents/dream-team-qa.toml', consumer / '.agents/skills/release',
                   consumer / '.codex/hooks.json']
        def remove_managed():
            for path in missing:
                path.unlink()
            (consumer / 'AGENTS.md').write_text('Regras do projeto.\n')
        remove_managed()
        state = project.reconcile(consumer, ROOT, state, ['codex', 'claude'], True, 'fixture2')
        self.assertTrue(all(path.is_symlink() or path.is_file() for path in missing))
        self.assertIn(project.START, (consumer / 'AGENTS.md').read_text())
        self.assertEqual(state['managed'], project.reconcile(consumer, ROOT, state, ['codex', 'claude'], True, 'fixture3')['managed'])
        remove_managed()
        disabled = project.reconcile(consumer, ROOT, state, ['codex', 'claude'], False, 'fixture3', disable=True)
        self.assertEqual(disabled['managed'], {})
        self.assertFalse(any(path.exists() or path.is_symlink() for path in missing))
        self.assertEqual((consumer / 'AGENTS.md').read_text(), 'Regras do projeto.\n')
        self.assertFalse((consumer / '.claude/agents/dream-team-qa.md').exists())

    def test_existing_bezalel_hook_without_record_is_not_duplicated(self):
        legacy = next(iter(project.LEGACY_HOOK_COMMANDS))
        for command in [project.HOOK_COMMAND, legacy]:
            with self.subTest(command=command):
                consumer = self.root / ('hook-' + str(len(command)))
                init(consumer)
                hook_path = consumer / '.codex/hooks.json'
                hook_path.parent.mkdir()
                config = {'hooks': {'SessionStart': [{'matcher': 'startup', 'hooks': [
                    {'type': 'command', 'command': command, 'timeout': 30}]}]}}
                hook_path.write_text(json.dumps(config))
                with self.assertRaises(dist.DistributionError):
                    project.reconcile(consumer, ROOT, {}, ['codex'], True, 'fixture')
                self.assertEqual(dist.read_json(hook_path), config)

    def test_customized_registered_hook_still_blocks_update(self):
        consumer = self.consumer()
        state = project.reconcile(consumer, ROOT, {}, ['codex'], True, 'fixture')
        hook_path = consumer / '.codex/hooks.json'
        config = dist.read_json(hook_path)
        config['hooks']['SessionStart'][0]['hooks'][0]['timeout'] = 5
        hook_path.write_text(json.dumps(config))
        with self.assertRaises(dist.DistributionError):
            project.reconcile(consumer, ROOT, state, ['codex'], True, 'fixture2')
        self.assertEqual(dist.read_json(hook_path), config)

    def test_worktree_links_main_base_through_hook_and_cli(self):
        source, consumer, base, state = self.connected()
        ignore = consumer / '.bezalel/.gitignore'
        ignore.write_text('/base/\n/install.local.json\n/update.lock\n')
        commit(consumer)
        def worktree(name):
            path = self.root / name
            dist.git(consumer, 'worktree', 'add', '-q', '-b', name, str(path))
            return path
        def cli(path):
            return subprocess.run([sys.executable, '-B', str(base / 'scripts/project.py'), 'link-worktree',
                                   '--project', str(path)], capture_output=True, text=True)
        first = worktree('corrigir-cli')
        self.assertFalse((first / '.agents/skills/release/SKILL.md').exists())
        result = cli(first)
        self.assertEqual(result.returncode, 1)
        self.assertFalse((first / '.bezalel/base').is_symlink())
        (first / '.bezalel/.gitignore').write_text('/base\n/install.local.json\n/update.lock\n')
        for _ in range(2):
            result = cli(first)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((first / '.agents/skills/release/SKILL.md').is_file())
        ignore.write_text('/base\n/install.local.json\n/update.lock\n')
        commit(consumer, 'Ignora link da base')
        second = worktree('corrigir-hook')
        result = subprocess.run(['sh', '-c', project.HOOK_COMMAND], cwd=second, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Worktree ligada', result.stdout)
        self.assertEqual(Path(os.readlink(second / '.bezalel/base')), base.resolve())
        self.assertTrue((second / '.claude/skills/clean-code/SKILL.md').is_file())
        self.assertEqual(dist.git(second, 'status', '--porcelain').strip(), b'')
        self.assertFalse((second / '.bezalel/install.local.json').exists())
        with self.assertRaises(subprocess.CalledProcessError):
            subprocess.run(['git', '-C', str(consumer), 'rev-parse', '--verify', '-q', 'HEAD:.bezalel/base'],
                           check=True, capture_output=True)

    def test_hook_is_silent_without_base(self):
        consumer = self.consumer()
        result = subprocess.run(['sh', '-c', project.HOOK_COMMAND], cwd=consumer, capture_output=True, text=True)
        self.assertEqual((result.returncode, result.stdout, result.stderr), (0, '', ''))

    def test_published_revision_adds_skill_and_updates_workflow_together(self):
        source, consumer, base, state = self.connected()
        path = source / 'skills/new-skill/SKILL.md'
        path.parent.mkdir()
        sections = ['Objetivo e escopo', 'Entradas e pré-requisitos', 'Procedimento', 'Saídas', 'Validação', 'Limites operacionais']
        path.write_text('---\nname: new-skill\ndescription: Fixture\n---\n' + ''.join('## ' + s + '\nTexto.\n' for s in sections))
        with (source / 'agents/dream-team.md').open('a') as stream:
            stream.write('\nNota sintética de versão.\n')
        revision = commit(source)
        self.assertTrue(project.update(consumer, state))
        self.assertEqual(dist.git(base, 'rev-parse', 'HEAD').decode().strip(), revision)
        self.assertTrue((consumer / '.agents/skills/new-skill/SKILL.md').is_file())
        self.assertIn('Nota sintética', (base / 'agents/dream-team.md').read_text())
        self.assertFalse(project.update(consumer, dist.read_json(consumer / project.STATE)))

    def test_update_refuses_dirty_source_without_fetch_or_discard(self):
        _, consumer, base, state = self.connected()
        (base / 'README.md').write_text('Personalizado')
        with self.assertRaisesRegex(dist.DistributionError, 'mudanças locais'):
            project.update(consumer, state)
        self.assertEqual((base / 'README.md').read_text(), 'Personalizado')

    def test_published_revision_renames_flow_references_together(self):
        source, consumer, base, state = self.connected()
        flow = dist.read_json(source / 'agents/catalog.json')['workflow']
        renamed = {flow['source']: 'fluxo-renomeado.md', flow['skills']: 'metodos-renomeados.md'}
        for path in [source / 'README.md', source / 'AGENTS.md', *(source / 'agents').rglob('*')]:
            if path.is_file() and path.suffix in {'.md', '.json', '.toml'}:
                content = path.read_text()
                for old, new in renamed.items():
                    content = content.replace(old, new)
                path.write_text(content)
        for old, new in renamed.items():
            (source / 'agents' / old).rename(source / 'agents' / new)
        revision = commit(source)
        self.assertTrue(project.update(consumer, state))
        for old, new in renamed.items():
            self.assertFalse((base / 'agents' / old).exists())
            self.assertTrue((base / 'agents' / new).is_file())
            for name in ['AGENTS.md', 'CLAUDE.md']:
                content = (consumer / name).read_text()
                self.assertIn('agents/' + new, content)
                self.assertNotIn('agents/' + old, content)
        self.assertEqual(dist.read_json(consumer / project.STATE)['revision'], revision)
        result = subprocess.run([sys.executable, '-B', str(base / 'scripts/project.py'),
                                 'status', '--project', str(consumer)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_invalid_remote_does_not_move_source_or_installation(self):
        source, consumer, base, state = self.connected()
        (source / 'agents/catalog.json').write_text('{}')
        commit(source)
        with self.assertRaises(dist.DistributionError):
            project.update(consumer, state)
        self.assertEqual(dist.git(base, 'rev-parse', 'HEAD').decode().strip(), state['revision'])
        self.assertEqual(dist.read_json(consumer / project.STATE), state)

    def test_published_agent_rename_replaces_both_platforms_without_duplicates(self):
        source, consumer, base, state = self.connected()
        previous = rename_agent(source, 'qa', 'quality-check')
        revision = commit(source)
        self.assertTrue(project.update(consumer, state))
        for platform, suffix in [('codex', '.toml'), ('claude', '.md')]:
            folder = consumer / ('.' + platform) / 'agents'
            self.assertFalse((folder / Path(previous[platform]).name).exists())
            self.assertIn('quality-check', (folder / ('quality-check' + suffix)).read_text())
            self.assertEqual(len(list(folder.glob('*' + suffix))), 9)
        self.assertEqual(dist.git(base, 'rev-parse', 'HEAD').decode().strip(), revision)
        self.assertIn('Regras do projeto.', (consumer / 'AGENTS.md').read_text())
        self.assertTrue((consumer / '.claude/commands/bezalel-release.md').is_file())

    def test_renaming_a_customized_agent_blocks_before_removing_it(self):
        source, consumer, base, state = self.connected()
        previous = rename_agent(source, 'qa', 'quality-check')
        commit(source)
        old = consumer / '.codex/agents' / Path(previous['codex']).name
        old.write_text('Minha customização')
        with self.assertRaises(dist.DistributionError):
            project.update(consumer, state)
        self.assertEqual(old.read_text(), 'Minha customização')
        self.assertFalse((consumer / '.codex/agents/quality-check.toml').exists())
        self.assertEqual(dist.git(base, 'rev-parse', 'HEAD').decode().strip(), state['revision'])
        self.assertEqual(dist.read_json(consumer / project.STATE), state)

    def test_agent_identity_must_match_filename_and_both_platforms(self):
        source = self.source()
        previous = rename_agent(source, 'qa', 'quality-check')
        with patch.object(check_repository, 'ROOT', source.resolve()):
            self.assertEqual(check_repository.validate_agents(), [])
            adapter = source / 'agents/codex/quality-check.toml'
            original = adapter.read_text()
            adapter.write_text(original.replace('name = "quality-check"', 'name = "wrong"'))
            self.assertTrue(check_repository.validate_agents())
            adapter.write_text(original)
            claude = source / 'agents/claude/quality-check.md'
            claude.rename(source / 'agents' / previous['claude'])
            catalog_path = source / 'agents/catalog.json'
            catalog = dist.read_json(catalog_path)
            catalog['roles']['qa']['claude'] = previous['claude']
            catalog_path.write_bytes(dist.json_bytes(catalog))
            self.assertTrue(check_repository.validate_agents())

    def test_network_failure_preserves_current_version(self):
        _, consumer, base, state = self.connected()
        dist.git(base, 'remote', 'set-url', 'origin', str(self.root / 'missing-remote'))
        with self.assertRaises(dist.DistributionError):
            project.update(consumer, state)
        self.assertEqual(dist.git(base, 'rev-parse', 'HEAD').decode().strip(), state['revision'])

    def test_git_operations_do_not_start_automatic_maintenance(self):
        consumer = self.consumer()
        settings = {
            'maintenance.auto': 'true',
            'maintenance.autoDetach': 'false',
            'maintenance.gc.enabled': 'false',
            'maintenance.commit-graph.enabled': 'true',
            'maintenance.commit-graph.auto': '-1',
        }
        for key, value in settings.items():
            dist.git(consumer, 'config', key, value)
        config_before = (consumer / '.git/config').read_bytes()
        trace = self.root / 'git-trace.json'
        with patch.dict(os.environ, {'GIT_TRACE2_EVENT': str(trace)}):
            commit(consumer)
        events = [json.loads(line) for line in trace.read_text().splitlines()]
        maintenance = [event for event in events if event.get('event') == 'child_start'
                       and any(arg in {'maintenance', 'gc'} for arg in event.get('argv', []))]
        self.assertEqual(maintenance, [], 'A operação iniciou manutenção automática do Git.')
        self.assertEqual((consumer / '.git/config').read_bytes(), config_before)

    def test_write_failure_rolls_back_managed_files(self):
        consumer = self.consumer()
        original = project.atomic_write
        calls = 0
        def failing(path, data, mode=0o644):
            nonlocal calls
            calls += 1
            if calls == 3:
                raise OSError('Fixture')
            return original(path, data, mode)
        with patch.object(project, 'atomic_write', side_effect=failing):
            with self.assertRaises(OSError):
                project.reconcile(consumer, ROOT, {}, ['codex'], False, 'fixture')
        self.assertEqual((consumer / 'AGENTS.md').read_text(), 'Regras do projeto.\n')
        self.assertFalse((consumer / project.STATE).exists())
        self.assertFalse(any(p.is_file() or p.is_symlink() for p in (consumer / '.agents').rglob('*')))

    def test_concurrent_edit_between_plan_and_apply_is_preserved(self):
        consumer = self.consumer()
        state = project.reconcile(consumer, ROOT, {}, ['codex'], False, 'fixture')
        entries = project.desired(consumer, ROOT, ['codex'], False)
        entries['AGENTS.md']['content'] += '\nMudança planejada.'
        changes, _ = project.plan(consumer, state['managed'], entries)
        with (consumer / 'AGENTS.md').open('a') as stream:
            stream.write('\nEdição concorrente.')
        with self.assertRaisesRegex(dist.DistributionError, 'durante'):
            project.apply(consumer, changes)
        self.assertIn('Edição concorrente.', (consumer / 'AGENTS.md').read_text())

    def test_native_hook_does_not_create_state_in_an_unconnected_project(self):
        consumer = self.consumer()
        argv = ['plugin.py', 'refresh', '--project', str(consumer), '--client', 'codex']
        with patch.object(sys, 'argv', argv):
            self.assertEqual(plugin.main(), 0)
        self.assertFalse((consumer / '.bezalel').exists())

    def test_native_cache_with_operational_state_cannot_auto_update(self):
        package = self.root / 'cache'
        state = package / 'skills/env/state/project/environment'
        state.mkdir(parents=True)
        (state / 'context.json').write_text('fixture')
        with self.assertRaisesRegex(dist.DistributionError, 'estado operacional'):
            plugin.check_runtime_state(package)
        self.assertEqual((state / 'context.json').read_text(), 'fixture')

    def test_remote_update_rolls_back_base_when_project_write_fails(self):
        source, consumer, base, state = self.connected()
        adapter = source / 'agents/codex/dream-team-qa.toml'
        adapter.write_text(adapter.read_text().replace('Você exerce', 'Nesta versão, você exerce'))
        commit(source)
        original = project.atomic_write
        failed = False
        def failing(path, data, mode=0o644):
            nonlocal failed
            # Falha a gravação final do registro, depois do checkout (o marcador pendente passa).
            if Path(path).name == 'install.local.json' and b'"pending"' not in data and not failed:
                failed = True
                raise OSError('Falha sintética na gravação do registro')
            return original(path, data, mode)
        with patch.object(project, 'atomic_write', side_effect=failing):
            with self.assertRaises(OSError):
                project.update(consumer, state)
        self.assertTrue(failed)
        self.assertEqual(dist.git(base, 'rev-parse', 'HEAD').decode().strip(), state['revision'])
        self.assertEqual(dist.read_json(consumer / project.STATE), state)
        self.assertNotIn('Nesta versão', (consumer / '.codex/agents/dream-team-qa.toml').read_text())

    def interrupted_update(self, target, mode):
        """Publica uma revisão e interrompe o update num processo filho."""
        source, consumer, base, state = self.connected()
        adapter = source / 'agents/codex/dream-team-qa.toml'
        adapter.write_text(adapter.read_text().replace('Você exerce', 'Nesta versão, você exerce'))
        claude = source / 'agents/claude/dream-team-qa.md'
        claude.write_text(claude.read_text() + '\nNesta versão.\n')
        skill = source / 'skills/nova-skill'
        skill.mkdir()
        sections = ['Objetivo e escopo', 'Entradas e pré-requisitos', 'Procedimento',
                    'Saídas', 'Validação', 'Limites operacionais']
        (skill / 'SKILL.md').write_text('---\nname: nova-skill\ndescription: Nova skill\n---\n'
                                        + ''.join('## ' + section + '\nTexto.\n' for section in sections))
        revision = commit(source, 'Nova versão')
        result = subprocess.run([sys.executable, '-B', '-c', INTERRUPTED_UPDATE, str(ROOT / 'scripts'),
                                 str(consumer), target, mode], capture_output=True, text=True, timeout=120)
        return consumer, base, state, revision, result

    def assert_updated(self, consumer, base, revision):
        head = dist.git(base, 'rev-parse', 'HEAD').decode().strip()
        recorded = dist.read_json(consumer / project.STATE)
        self.assertEqual((head, recorded['revision']), (revision, revision))
        self.assertNotIn('pending', recorded)
        entries = project.desired(consumer, base, recorded['platforms'], recorded['automatic'])
        self.assertEqual(project.plan(consumer, recorded['managed'], entries)[0], {})
        self.assertTrue((consumer / '.agents/skills/nova-skill/SKILL.md').is_file())
        self.assertIn('Nesta versão', (consumer / '.codex/agents/dream-team-qa.toml').read_text())
        self.assertIn('Nesta versão', (consumer / '.claude/agents/dream-team-qa.md').read_text())

    def test_update_killed_before_final_record_is_completed_by_next_run(self):
        consumer, base, state, revision, result = self.interrupted_update('install.local.json', 'kill')
        self.assertEqual(result.returncode, -9, result.stderr)
        self.assertEqual(dist.git(base, 'rev-parse', 'HEAD').decode().strip(), revision)
        self.assertTrue(project.update(consumer, dist.read_json(consumer / project.STATE)))
        self.assert_updated(consumer, base, revision)

    def test_update_killed_midway_through_project_files_is_completed(self):
        consumer, base, state, revision, result = self.interrupted_update('.codex/agents/dream-team-qa.toml', 'kill')
        self.assertEqual(result.returncode, -9, result.stderr)
        # Gravação parcial: o adaptador Claude já mudou e o do Codex ainda não.
        self.assertIn('Nesta versão', (consumer / '.claude/agents/dream-team-qa.md').read_text())
        self.assertNotIn('Nesta versão', (consumer / '.codex/agents/dream-team-qa.toml').read_text())
        self.assertTrue(project.update(consumer, dist.read_json(consumer / project.STATE)))
        self.assert_updated(consumer, base, revision)

    def test_update_killed_before_checkout_retries_from_origin(self):
        consumer, base, state, revision, result = self.interrupted_update('checkout', 'kill')
        self.assertEqual(result.returncode, -9, result.stderr)
        self.assertEqual(dist.git(base, 'rev-parse', 'HEAD').decode().strip(), state['revision'])
        self.assertTrue(project.update(consumer, dist.read_json(consumer / project.STATE)))
        self.assert_updated(consumer, base, revision)

    def test_sigterm_during_update_rolls_back_files_base_and_record(self):
        for target in ['.codex/agents/dream-team-qa.toml', 'checkout']:
            with self.subTest(target=target):
                self.root = Path(self.temp.name) / Path(target).stem
                self.root.mkdir()
                consumer, base, state, revision, result = self.interrupted_update(target, 'term')
                self.assertEqual(result.returncode, 3, result.stderr)
                self.assertIn('interrompida por sinal', result.stderr)
                self.assertEqual(dist.git(base, 'rev-parse', 'HEAD').decode().strip(), state['revision'])
                self.assertEqual(dist.read_json(consumer / project.STATE), state)
                self.assertNotIn('Nesta versão', (consumer / '.claude/agents/dream-team-qa.md').read_text())
                self.assertFalse((consumer / '.agents/skills/nova-skill').is_symlink())
                self.assertTrue(project.update(consumer, state))
                self.assert_updated(consumer, base, revision)

    def test_reformatted_hook_config_is_neither_divergent_nor_rewritten(self):
        consumer = self.consumer()
        state = project.reconcile(consumer, ROOT, {}, ['codex', 'claude'], True, 'fixture')
        names = ['.claude/settings.local.json', '.codex/hooks.json']
        for name in names:
            path = consumer / name
            path.write_text(json.dumps(dist.read_json(path), indent=4, sort_keys=True), encoding='utf-8')
        before = {name: (consumer / name).read_bytes() for name in names}
        entries = project.desired(consumer, ROOT, ['codex', 'claude'], True)
        self.assertEqual(project.plan(consumer, state['managed'], entries)[0], {})
        project.reconcile(consumer, ROOT, state, ['codex', 'claude'], True, 'fixture2')
        self.assertEqual({name: (consumer / name).read_bytes() for name in names}, before)

    def test_disable_removes_only_hook_containers_created_by_installer(self):
        unrelated = {'hooks': [{'type': 'command', 'command': 'fixture-command'}]}
        cases = {
            'ausente': None,
            'proprio': {'permissions': {'allow': ['Read']}},
            'lista-do-usuario': {'hooks': {'SessionStart': []}},
            'outros-hooks': {'hooks': {'SessionStart': [unrelated], 'Stop': []}},
        }
        for label, original in cases.items():
            with self.subTest(case=label):
                consumer = self.root / label
                init(consumer)
                path = consumer / '.claude/settings.local.json'
                if original is not None:
                    path.parent.mkdir()
                    path.write_text(json.dumps(original), encoding='utf-8')
                state = project.reconcile(consumer, ROOT, {}, ['claude'], True, 'fixture')
                state = project.reconcile(consumer, ROOT, state, ['claude'], True, 'fixture2')
                project.reconcile(consumer, ROOT, state, ['claude'], False, 'fixture2', disable=True)
                if original is None:
                    self.assertFalse(path.exists())
                else:
                    self.assertEqual(dist.read_json(path), original)

    def test_enable_then_disable_restores_instruction_files_byte_for_byte(self):
        originals = {
            'AGENTS.md': 'Regras do projeto — ação.\r\nSegunda linha.\r\n'.encode('utf-8'),
            'README.md': 'Conteúdo próprio sem quebra final'.encode('utf-8'),
            'CLAUDE.md': b'\xef\xbb\xbf' + 'Instruções próprias.\n'.encode('utf-8'),
        }
        for label, files in [('existentes', originals), ('ausentes', {})]:
            with self.subTest(case=label):
                consumer = self.root / label
                init(consumer)
                for name, data in files.items():
                    (consumer / name).write_bytes(data)
                state = project.reconcile(consumer, ROOT, {}, ['codex', 'claude'], True, 'fixture')
                agents = (consumer / 'AGENTS.md').read_bytes()
                self.assertIn(project.START.encode(), agents)
                if files:
                    self.assertTrue(agents.startswith(originals['AGENTS.md']))
                    self.assertEqual(agents.count(b'\n'), agents.count(b'\r\n'), 'CRLF não preservado')
                    self.assertTrue((consumer / 'CLAUDE.md').read_bytes().startswith(originals['CLAUDE.md']))
                state = project.reconcile(consumer, ROOT, state, ['codex', 'claude'], True, 'fixture2')
                self.assertEqual((consumer / 'AGENTS.md').read_bytes(), agents)
                project.reconcile(consumer, ROOT, state, ['codex', 'claude'], False, 'fixture2', disable=True)
                for name in ['AGENTS.md', 'README.md', 'CLAUDE.md']:
                    if name in files:
                        self.assertEqual((consumer / name).read_bytes(), files[name], name)
                    else:
                        self.assertFalse((consumer / name).exists(), name)

    def test_installer_scripts_read_and_write_text_as_utf8(self):
        for name in ['distribution.py', 'project.py', 'plugin.py']:
            tree = ast.parse((ROOT / 'scripts' / name).read_text(encoding='utf-8'))
            for node in ast.walk(tree):
                if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
                    continue
                keywords = {keyword.arg for keyword in node.keywords}
                if node.func.attr in {'read_text', 'write_text'}:
                    self.assertIn('encoding', keywords, f'{name}:{node.lineno}')
                archive = isinstance(node.func.value, ast.Name) and node.func.value.id == 'tarfile'
                if node.func.attr in {'open', 'fdopen'} and not archive:
                    modes = [arg.value for arg in node.args if isinstance(arg, ast.Constant) and isinstance(arg.value, str)]
                    self.assertTrue('encoding' in keywords or any('b' in mode for mode in modes), f'{name}:{node.lineno}')

    def test_rewritten_remote_history_is_not_forced_onto_project(self):
        source, consumer, base, state = self.connected()
        dist.git(source, 'checkout', '--orphan', 'replacement')
        (source / 'README.md').write_text('Outra origem')
        commit(source)
        dist.git(source, 'branch', '-M', 'master')
        with self.assertRaises(dist.DistributionError):
            project.update(consumer, state)
        self.assertEqual(dist.git(base, 'rev-parse', 'HEAD').decode().strip(), state['revision'])

    def test_bundle_is_versioned_and_preserves_original_skills(self):
        source = self.source()
        package = self.root / 'plugin'
        v1 = plugin.build(source, package)
        self.assertEqual(dist.files(package / 'skills'), dist.files(source / 'skills'))
        claude = dist.read_json(package / '.claude-plugin/plugin.json')
        self.assertEqual(len(claude['agents']), 9)
        self.assertNotIn('./skills/release', claude['skills'])
        self.assertIn('./commands/bezalel-release.md', claude['commands'])
        self.assertNotIn('hooks/hooks.json', dist.files(package))
        self.assertIn('${CLAUDE_PLUGIN_ROOT}', (package / 'contracts/claude/dream-team-qa.md').read_text())
        self.assertIn('contracts/processes/qa.md', (package / 'contracts/codex/dream-team-qa.toml').read_text())
        self.assertTrue((package / 'contracts/processes/qa.md').is_file())
        self.assertFalse((package / 'agents').exists())
        with (source / 'agents/dream-team.md').open('a') as stream:
            stream.write('\nNova versão\n')
        v2 = plugin.build(source, self.root / 'plugin2')
        self.assertNotEqual(v1, v2)
        with self.assertRaises(dist.DistributionError):
            plugin.build(source, package)

    def test_native_binding_tracks_loaded_package_and_protects_custom_agents(self):
        package = self.root / 'plugin'
        plugin.build(ROOT, package)
        consumer = self.consumer()
        state = plugin.bind(consumer, package, {}, ['codex', 'claude'], True)
        self.assertEqual((consumer / '.bezalel/base').resolve(), package.resolve())
        self.assertFalse((consumer / '.agents/skills').exists())
        self.assertFalse((consumer / '.claude/agents').exists())
        self.assertTrue((consumer / '.codex/agents/dream-team-qa.toml').is_file())
        (consumer / '.codex/agents/dream-team-qa.toml').write_text('Meu agente')
        with self.assertRaises(dist.DistributionError):
            plugin.bind(consumer, package, state, ['codex', 'claude'], True)

    def test_native_update_replaces_renamed_agent_and_rebinds_new_package(self):
        source = self.source()
        package = self.root / 'plugin'
        plugin.build(source, package)
        consumer = self.consumer()
        state = plugin.bind(consumer, package, {}, ['codex', 'claude'], True)
        previous = rename_agent(source, 'qa', 'quality-check')
        updated = self.root / 'updated-plugin'
        plugin.build(source, updated)
        plugin.bind(consumer, updated, state, ['codex', 'claude'], True)
        self.assertEqual((consumer / '.bezalel/base').resolve(), updated.resolve())
        self.assertFalse((consumer / '.codex/agents' / Path(previous['codex']).name).exists())
        self.assertTrue((consumer / '.codex/agents/quality-check.toml').is_file())
        self.assertEqual(len(list((consumer / '.codex/agents').glob('*.toml'))), 9)
        manifest = dist.read_json(updated / '.claude-plugin/plugin.json')
        self.assertIn('./contracts/claude/quality-check.md', manifest['agents'])
        self.assertNotIn('./contracts/' + previous['claude'], manifest['agents'])

    def packages(self):
        """Dois pacotes nativos da mesma fonte: o anterior e o novo."""
        source = self.source()
        old, new = self.root / 'plugin-old', self.root / 'plugin-new'
        plugin.build(source, old)
        with (source / 'agents/dream-team.md').open('a', encoding='utf-8') as stream:
            stream.write('\nNova versão\n')
        plugin.build(source, new)
        return old.resolve(), new.resolve()

    def refresh(self, consumer, package, client, failing=False):
        """Executa o hook nativo do aplicativo `client`, com `package` como cache carregado."""
        real = subprocess.run
        def run(command, *args, **kwargs):
            if command[0] in {'codex', 'claude'}:
                if failing:
                    raise subprocess.CalledProcessError(1, command)
                return subprocess.CompletedProcess(command, 0, b'', b'')
            return real(command, *args, **kwargs)
        output = io.StringIO()
        argv = ['plugin.py', 'refresh', '--project', str(consumer), '--client', client]
        with patch.object(sys, 'argv', argv), patch.object(plugin, 'ROOT', package), \
                patch.object(subprocess, 'run', side_effect=run), \
                contextlib.redirect_stdout(output), contextlib.redirect_stderr(io.StringIO()):
            code = plugin.main()
        return code, output.getvalue()

    def test_native_refresh_rebinds_only_from_owner_and_never_regresses(self):
        old, new = self.packages()
        consumer = self.consumer()
        plugin.bind(consumer, old, {}, ['codex', 'claude'], True)
        base = consumer / '.bezalel/base'
        # Claude já na versão nova e Codex ainda na anterior, alternando sessões.
        steps = [('claude', new), ('codex', old), ('claude', new), ('codex', new), ('claude', old), ('codex', new)]
        targets, outputs = [], []
        for client, package in steps:
            code, output = self.refresh(consumer, package, client)
            self.assertEqual(code, 0)
            targets.append(base.resolve())
            outputs.append(output)
        self.assertEqual(targets, [old, old, old, new, new, new])
        self.assertIn('seguem a versão', outputs[0])
        self.assertIn('contratos e agentes atualizados', outputs[3])
        self.assertEqual([outputs[i] for i in (1, 2, 5)], ['', '', ''])
        recorded = dist.read_json(consumer / plugin.STATE)
        self.assertEqual(recorded['version'], dist.read_json(new / 'plugin.json')['version'])
        self.assertEqual(recorded['versions'], {'codex': recorded['version'],
                                                'claude': dist.read_json(old / 'plugin.json')['version']})

    def test_native_refresh_records_state_only_after_update_commands(self):
        old, new = self.packages()
        consumer = self.consumer()
        plugin.bind(consumer, old, {}, ['codex'], True)
        before = dist.read_json(consumer / plugin.STATE)
        code, output = self.refresh(consumer, new, 'codex', failing=True)
        self.assertEqual((code, output), (1, ''))
        self.assertEqual((consumer / '.bezalel/base').resolve(), old)
        self.assertEqual(dist.read_json(consumer / plugin.STATE), before)
        code, output = self.refresh(consumer, new, 'codex')
        self.assertEqual(code, 0)
        self.assertIn('contratos e agentes atualizados', output)
        self.assertEqual((consumer / '.bezalel/base').resolve(), new)
        self.assertEqual(self.refresh(consumer, new, 'codex'), (0, ''))

    def test_refresh_is_scoped_to_bezalel_and_never_runs_skill_commands(self):
        for client in ['codex', 'claude']:
            commands = plugin.refresh_commands(client)
            self.assertEqual(len(commands), 2)
            self.assertTrue(all(c[0] == client and 'plugin' in c for c in commands))
            self.assertIn('bezalel@bezalel', commands[1])
        with self.assertRaises(dist.DistributionError):
            plugin.refresh_commands('other')

    def test_project_cli_installs_reports_and_disables_in_isolation(self):
        source, consumer = self.source(), self.consumer()
        base = consumer / '.bezalel/base'
        dist.git(consumer, 'clone', '-q', '--', str(source), str(base))
        context = consumer / '.bezalel/project.json'
        context.write_text('{"custom": "preservar"}')
        for action in ['enable', 'status', 'disable']:
            result = subprocess.run([sys.executable, '-B', str(base / 'scripts/project.py'), action,
                                     '--project', str(consumer)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(context.read_text(), '{"custom": "preservar"}')
        self.assertIn('/base', (consumer / '.bezalel/.gitignore').read_text().splitlines())
        self.assertFalse((consumer / '.codex/agents/dream-team-qa.toml').exists())


class UpstreamTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.upstream = self.root / 'upstream'
        init(self.upstream)
        skill = self.upstream / 'humanizer'
        skill.mkdir()
        (skill / 'SKILL.md').write_text('original\n')
        (skill / 'old.md').write_text('old\n')
        self.original_revision = commit(self.upstream)
        self.local = self.root / 'local'
        shutil.copytree(skill, self.local / 'skills/humanizer')
        manifest = {'schema_version': 1, 'skills': {'humanizer': {
            'revision': self.original_revision, 'preserve': [], 'mode_overrides': {},
            'files': dist.fingerprints(dist.files(self.local / 'skills/humanizer'))}}}
        (self.local / '.bezalel').mkdir()
        (self.local / sync_upstream.MANIFEST).write_bytes(dist.json_bytes(manifest))

    def test_changed_upstream_updates_adds_and_removes_original_files(self):
        (self.upstream / 'humanizer/SKILL.md').write_text('updated\n')
        (self.upstream / 'humanizer/old.md').unlink()
        (self.upstream / 'humanizer/new.md').write_text('new\n')
        revision = commit(self.upstream)
        report = sync_upstream.synchronize(self.local, self.upstream, 'HEAD', True)
        self.assertEqual(report['updated'], ['humanizer'])
        self.assertFalse((self.local / 'skills/humanizer/old.md').exists())
        self.assertEqual((self.local / 'skills/humanizer/new.md').read_text(), 'new\n')
        self.assertEqual(dist.read_json(self.local / sync_upstream.MANIFEST)['skills']['humanizer']['revision'], revision)
        self.assertEqual(sync_upstream.synchronize(self.local, self.upstream, 'HEAD', True)['updated'], [])

    def test_local_edits_or_extra_files_protect_whole_skill(self):
        (self.local / 'skills/humanizer/my-rule.md').write_text('regra local\n')
        (self.upstream / 'humanizer/SKILL.md').write_text('updated\n')
        commit(self.upstream)
        report = sync_upstream.synchronize(self.local, self.upstream, 'HEAD', True)
        self.assertEqual(report['protected'], ['humanizer'])
        self.assertEqual((self.local / 'skills/humanizer/SKILL.md').read_text(), 'original\n')

    def test_dry_run_does_not_write(self):
        (self.upstream / 'humanizer/SKILL.md').write_text('updated\n')
        commit(self.upstream)
        before = dist.files(self.local)
        report = sync_upstream.synchronize(self.local, self.upstream, 'HEAD')
        self.assertEqual(report['updated'], ['humanizer'])
        self.assertEqual(dist.files(self.local), before)

    def test_upstream_symlink_or_missing_skill_aborts_before_mutation(self):
        (self.upstream / 'humanizer/SKILL.md').unlink()
        (self.upstream / 'humanizer/SKILL.md').symlink_to('/etc/passwd')
        commit(self.upstream)
        before = dist.files(self.local)
        with self.assertRaises(dist.DistributionError):
            sync_upstream.synchronize(self.local, self.upstream, 'HEAD', True)
        self.assertEqual(dist.files(self.local), before)

    def test_manual_metadata_overlay_is_kept_while_original_procedure_updates(self):
        metadata = self.local / 'skills/humanizer/agents/openai.yaml'
        metadata.parent.mkdir()
        metadata.write_text('policy:\n  allow_implicit_invocation: false\n')
        manifest = dist.read_json(self.local / sync_upstream.MANIFEST)
        entry = manifest['skills']['humanizer']
        entry['preserve'] = ['agents/openai.yaml']
        entry['files'] = dist.fingerprints(dist.files(self.local / 'skills/humanizer'))
        (self.local / sync_upstream.MANIFEST).write_bytes(dist.json_bytes(manifest))
        (self.upstream / 'humanizer/SKILL.md').write_text('updated\n')
        commit(self.upstream)
        sync_upstream.synchronize(self.local, self.upstream, 'HEAD', True)
        self.assertIn('false', metadata.read_text())
        self.assertEqual((self.local / 'skills/humanizer/SKILL.md').read_text(), 'updated\n')

    def test_adapted_skills_cannot_be_added_to_automatic_selection(self):
        manifest = dist.read_json(self.local / sync_upstream.MANIFEST)
        manifest['skills']['pr-audit'] = copy.deepcopy(manifest['skills']['humanizer'])
        (self.local / sync_upstream.MANIFEST).write_bytes(dist.json_bytes(manifest))
        with self.assertRaisesRegex(dist.DistributionError, 'adaptação'):
            sync_upstream.synchronize(self.local, self.upstream, 'HEAD', True)


if __name__ == '__main__':
    unittest.main()
