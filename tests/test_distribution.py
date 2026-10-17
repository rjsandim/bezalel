"""Distribuição em repositórios sintéticos; não instala plugins ou chama serviços."""
import copy
import json
import os
from pathlib import Path
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


def commit(root, message='Fixture'):
    dist.git(root, 'add', '-A')
    dist.git(root, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', message)
    return dist.git(root, 'rev-parse', 'HEAD').decode().strip()


def init(root):
    root.mkdir(parents=True, exist_ok=True)
    dist.git(root, 'init', '-q', '-b', 'master')


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
        self.assertEqual(len(list((consumer / '.codex/agents').glob('*.toml'))), 9)
        self.assertEqual(len(list((consumer / '.claude/agents').glob('*.md'))), 9)
        self.assertTrue((consumer / 'AGENTS.md').read_text().startswith('Regras do projeto.'))
        self.assertIn('startup', json.dumps(state['managed']))

    def test_existing_agent_and_broken_link_are_not_adopted_or_overwritten(self):
        for kind in ['file', 'broken-link']:
            with self.subTest(kind=kind):
                consumer = self.root / kind
                path = consumer / '.codex/agents/bezalel-qa.toml'
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
        path = consumer / '.codex/agents/bezalel-qa.toml'
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
        self.assertFalse((consumer / '.codex/agents/bezalel-qa.toml').exists())
        self.assertFalse((consumer / '.agents/skills/release').is_symlink())
        self.assertNotIn(project.START, (consumer / 'AGENTS.md').read_text())
        self.assertIn('Regras do projeto.', (consumer / 'AGENTS.md').read_text())
        self.assertEqual((consumer / '.bezalel/project.json').read_text(), 'contexto próprio')

    def test_published_revision_adds_skill_and_updates_workflow_together(self):
        source, consumer, base, state = self.connected()
        path = source / 'skills/new-skill/SKILL.md'
        path.parent.mkdir()
        sections = ['Objetivo e escopo', 'Entradas e pré-requisitos', 'Procedimento', 'Saídas', 'Validação', 'Limites operacionais']
        path.write_text('---\nname: new-skill\ndescription: Fixture\n---\n' + ''.join('## ' + s + '\nTexto.\n' for s in sections))
        with (source / 'agents/company-flow-v2.md').open('a') as stream:
            stream.write('\nNota sintética de versão.\n')
        revision = commit(source)
        self.assertTrue(project.update(consumer, state))
        self.assertEqual(dist.git(base, 'rev-parse', 'HEAD').decode().strip(), revision)
        self.assertTrue((consumer / '.agents/skills/new-skill/SKILL.md').is_file())
        self.assertIn('Nota sintética', (base / 'agents/company-flow-v2.md').read_text())
        self.assertFalse(project.update(consumer, dist.read_json(consumer / project.STATE)))

    def test_update_refuses_dirty_source_without_fetch_or_discard(self):
        _, consumer, base, state = self.connected()
        (base / 'README.md').write_text('Personalizado')
        with self.assertRaisesRegex(dist.DistributionError, 'mudanças locais'):
            project.update(consumer, state)
        self.assertEqual((base / 'README.md').read_text(), 'Personalizado')

    def test_invalid_remote_does_not_move_source_or_installation(self):
        source, consumer, base, state = self.connected()
        (source / 'agents/catalog.json').write_text('{}')
        commit(source)
        with self.assertRaises(dist.DistributionError):
            project.update(consumer, state)
        self.assertEqual(dist.git(base, 'rev-parse', 'HEAD').decode().strip(), state['revision'])
        self.assertEqual(dist.read_json(consumer / project.STATE), state)

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
        adapter = source / 'agents/codex/bezalel-qa.toml'
        adapter.write_text(adapter.read_text().replace('Você exerce', 'Nesta versão, você exerce'))
        commit(source)
        original = project.atomic_write
        failed = False
        def failing(path, data, mode=0o644):
            nonlocal failed
            if Path(path).name == 'install.local.json' and not failed:
                failed = True
                raise OSError('Falha sintética na gravação do registro')
            return original(path, data, mode)
        with patch.object(project, 'atomic_write', side_effect=failing):
            with self.assertRaises(OSError):
                project.update(consumer, state)
        self.assertEqual(dist.git(base, 'rev-parse', 'HEAD').decode().strip(), state['revision'])
        self.assertEqual(dist.read_json(consumer / project.STATE), state)
        self.assertNotIn('Nesta versão', (consumer / '.codex/agents/bezalel-qa.toml').read_text())

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
        self.assertIn('${CLAUDE_PLUGIN_ROOT}', (package / 'contracts/claude/bezalel-qa.md').read_text())
        self.assertFalse((package / 'agents').exists())
        with (source / 'agents/company-flow-v2.md').open('a') as stream:
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
        self.assertTrue((consumer / '.codex/agents/bezalel-qa.toml').is_file())
        (consumer / '.codex/agents/bezalel-qa.toml').write_text('Meu agente')
        with self.assertRaises(dist.DistributionError):
            plugin.bind(consumer, package, state, ['codex', 'claude'], True)

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
        self.assertIn('/base/', (consumer / '.bezalel/.gitignore').read_text())
        self.assertFalse((consumer / '.codex/agents/bezalel-qa.toml').exists())


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
