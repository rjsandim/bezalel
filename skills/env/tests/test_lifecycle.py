"""Exercise public env commands with real Compose validation and simulated processes."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1]
DOCKER = shutil.which('docker')

FAKE_DOCKER = r'''#!/usr/bin/env python3
import json, os, subprocess, sys
from pathlib import Path
args = sys.argv[1:]
state_path = Path(os.environ['ENV_TEST_STATE'])
state = json.loads(state_path.read_text())
state['calls'].append(args)
state_path.write_text(json.dumps(state))
if args[0] == 'context':
    if os.environ.get('ENV_TEST_FAIL_CONTEXT') == '1':
        sys.exit(6)
    if args[1] == 'show':
        print('fixture')
    sys.exit(0)
if args[0] == 'start':
    if os.environ.get('ENV_TEST_FAIL_PROXY') == '1':
        sys.exit(8)
    sys.exit(0)
if args[:2] == ['volume', 'ls']:
    sys.exit(0)
if args == ['ps', '-aq']:
    if os.environ.get('ENV_TEST_SHARED_VOLUME') == '1':
        print('other-container')
    sys.exit(0)
if args[0] == 'inspect':
    print(json.dumps({'project': 'another-project', 'mounts': [{'Name': 'fixture-check_dbdata'}]}))
    sys.exit(0)
if args[0] != 'compose':
    sys.exit('Unexpected Docker operation: ' + repr(args))
file = args[2]
command = args[3]
rest = args[4:]
if os.environ.get('ENV_TEST_PRIVATE_DIAGNOSTIC') == '1':
    print('private-diagnostic-value', file=sys.stderr)
if command == 'config':
    os.execv(os.environ['ENV_TEST_DOCKER'], [os.environ['ENV_TEST_DOCKER'], *args])
if command == 'ps':
    if '--services' in rest:
        print('\n'.join(state['running']))
    sys.exit(0)
if command == 'up':
    if os.environ.get('ENV_TEST_FAIL_UP') == '1':
        sys.exit(7)
    config = json.loads(subprocess.check_output([os.environ['ENV_TEST_DOCKER'], 'compose', '-f', file, 'config', '--format', 'json']))
    wanted = [arg for arg in rest if arg in config['services']]
    if not wanted:
        sys.exit('Refusing untargeted startup')
    def start(name):
        for dependency in config['services'][name].get('depends_on', {}):
            start(dependency)
        if name not in state['running']:
            state['running'].append(name)
            state['ids'].setdefault(name, len(state['ids']) + 1)
    for name in wanted:
        start(name)
elif command == 'stop':
    state['running'] = []
elif command == 'down':
    if os.environ.get('ENV_TEST_FAIL_DOWN') == '1':
        sys.exit(9)
    state['running'] = []
elif command != 'restart':
    sys.exit('Unexpected Compose command: ' + command)
state_path.write_text(json.dumps(state))
'''

class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='env-lifecycle-')
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.skill = self.base / 'skill'
        for name in ('scripts', 'templates'):
            shutil.copytree(SKILL / name, self.skill / name)
        self.repo = self.base / 'project'
        self.repo.mkdir()
        stack = self.repo / '.envstack'
        stack.mkdir()
        (stack / 'stack.yaml').write_text('''project: fixture
engine: auto
docker_context: fixture
database: mysql
tld: local
startup:
  services: [api]
services:
  - {folder: api, type: php, port: 8000, database: true}
  - {folder: site, type: node, port: 5173, database: false, depends_on: [api]}
  - {folder: docs, type: node, port: 5173, database: false, depends_on: []}
''')
        for service in ('api', 'site', 'docs'):
            (self.repo / service).mkdir()
            (self.repo / service / 'sentinel.txt').write_text('work in progress\n')
            (stack / f'{service}.env.example').write_text('APP_NAME=${env:name}\nLOCAL_SETTING=original\n')
            (stack / f'{service}.Dockerfile').write_text('FROM busybox\n')
        self.run_process(['git', 'init', '-b', 'main'])
        self.run_process(['git', 'config', 'core.hooksPath', '/dev/null'])
        self.run_process(['git', 'add', '.'])
        self.run_process(['git', '-c', 'user.name=Env Test', '-c', 'user.email=env@example.invalid', '-c', 'core.hooksPath=/dev/null', 'commit', '-m', 'fixture'])
        self.state = self.base / 'docker-state.json'
        self.state.write_text(json.dumps({'running': [], 'ids': {}, 'calls': []}))
        bindir = self.base / 'bin'
        bindir.mkdir()
        (bindir / 'docker').write_text(FAKE_DOCKER)
        (bindir / 'docker').chmod(0o755)
        for forbidden in ['brew', 'sudo', 'mkcert']:
            sentinel = bindir / forbidden
            sentinel.write_text('#!/bin/sh\necho "Forbidden real infrastructure command" >&2\nexit 99\n')
            sentinel.chmod(0o755)
        self.env = {**os.environ, 'PATH': str(bindir) + os.pathsep + os.environ['PATH'], 'ENV_TEST_STATE': str(self.state), 'ENV_TEST_DOCKER': DOCKER, 'ENV_ALLOW_SHARED_INFRA': '1'}
        self.command('new.sh', 'check', extra={'ENV_DRY_RUN': '1'})
        self.worktree = self.repo / '.worktrees/check'
        self.compose = self.skill / 'state/fixture/check/docker-compose.yml'

    def run_process(self, args, **kw):
        result = subprocess.run(args, cwd=self.repo, text=True, capture_output=True, **kw)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def command(self, script, *args, extra=None, expected=0):
        result = subprocess.run(['bash', str(self.skill / 'scripts' / script), *args], cwd=self.repo, env={**self.env, **(extra or {})}, text=True, capture_output=True)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def observed(self):
        return json.loads(self.state.read_text())

    def test_audited_renamed_worktree_branch_remains_updatable(self):
        self.run_process(['git', '-C', str(self.worktree), 'branch', '-m', 'feature/renamed'])
        (self.compose.parent / 'worktree-branch').write_text('feature/renamed\n')
        self.command('update.sh', 'check', extra={'ENV_DRY_RUN': '1'})
        self.assertEqual((self.compose.parent / 'worktree-branch').read_text(), 'feature/renamed\n')

    def test_default_then_documentation_then_resume_preserves_work(self):
        self.command('ctl.sh', 'start', 'check')
        self.assertEqual(set(self.observed()['running']), {'api', 'mysql', 'redis'})
        ids = self.observed()['ids'].copy()
        envfile = self.worktree / 'api/.env'
        envfile.write_text('LOCAL_SETTING=edited by user\n')
        source = self.worktree / 'api/sentinel.txt'
        source.write_text('uncommitted edits\n')
        self.command('ctl.sh', 'ensure', 'check', 'docs', 'site')
        self.assertEqual(set(self.observed()['running']), {'api', 'mysql', 'redis', 'docs', 'site'})
        self.assertEqual({k: self.observed()['ids'][k] for k in ids}, ids)
        self.command('ctl.sh', 'stop', 'check')
        self.assertEqual(self.observed()['running'], [])
        self.command('ctl.sh', 'start', 'check')
        self.assertEqual(len(self.observed()['running']), 5)
        self.assertEqual(envfile.read_text(), 'LOCAL_SETTING=edited by user\n')
        self.assertEqual(source.read_text(), 'uncommitted edits\n')
        calls = self.observed()['calls']
        self.assertFalse(any('down' in call or '--remove-orphans' in call for call in calls))
        self.assertTrue(all('--no-recreate' in call for call in calls if 'up' in call))

    def test_repeat_new_and_update_keep_local_env_and_selected_services(self):
        self.command('ctl.sh', 'start', 'check')
        envfile = self.worktree / 'api/.env'
        envfile.write_text('LOCAL_SETTING=keep-me\n')
        self.command('new.sh', 'check', 'docs')
        self.command('update.sh', 'check', extra={'ENV_DRY_RUN': '1'})
        self.assertEqual(envfile.read_text(), 'LOCAL_SETTING=keep-me\n')
        self.assertNotIn('site', self.observed()['running'])

    def test_invalid_service_fails_before_mutation(self):
        before = self.observed()['calls']
        result = self.command('ctl.sh', 'ensure', 'check', 'missing', expected=1)
        self.assertIn('ausente', result.stderr)
        new_calls = self.observed()['calls'][len(before):]
        self.assertFalse(any('up' in call or call[0] == 'start' for call in new_calls))

    def test_compose_failure_preserves_private_diagnostic_without_echoing_values(self):
        result = self.command('ctl.sh', 'start', 'check', extra={'ENV_TEST_FAIL_UP': '1', 'ENV_TEST_PRIVATE_DIAGNOSTIC': '1'}, expected=7)
        self.assertNotIn('private-diagnostic-value', result.stdout + result.stderr)
        self.assertIn('codigo 7', result.stderr)
        diagnostics = list(self.compose.parent.glob('compose-diagnostic.*'))
        self.assertTrue(any('private-diagnostic-value' in file.read_text() for file in diagnostics))
        self.assertTrue(all(file.stat().st_mode & 0o777 == 0o600 for file in diagnostics))

    def test_start_failure_propagates_and_does_not_report_ready(self):
        result = self.command('ctl.sh', 'start', 'check', extra={'ENV_TEST_FAIL_UP': '1'}, expected=7)
        self.assertNotIn('dependencias prontos', result.stdout)
        self.assertFalse((self.compose.parent / 'started-services').exists())

    def test_docs_only_does_not_start_database_and_all_remains_available(self):
        self.command('ctl.sh', 'start', 'check', 'docs')
        self.assertEqual(self.observed()['running'], ['docs'])
        self.command('ctl.sh', 'start', 'check', '--all')
        self.assertEqual(len(self.observed()['running']), 5)

    def test_restart_keeps_dormant_services_off(self):
        self.command('ctl.sh', 'start', 'check')
        self.command('ctl.sh', 'restart', 'check')
        self.assertEqual(set(self.observed()['running']), {'api', 'mysql', 'redis'})

    def test_legacy_compose_without_startup_keeps_full_start(self):
        subprocess.run(['yq', '-i', 'del(.x-envstack)', str(self.compose)], check=True)
        self.command('ctl.sh', 'start', 'check')
        self.assertEqual(len(self.observed()['running']), 5)

    def test_invalid_update_preserves_previous_compose(self):
        before = self.compose.read_bytes()
        manifest = self.repo / '.envstack/stack.yaml'
        manifest.write_text(manifest.read_text().replace('depends_on: [api]', 'depends_on: [missing]'))
        result = subprocess.run(['bash', str(self.skill / 'scripts/update.sh'), 'check'], cwd=self.repo, env={**self.env, 'ENV_DRY_RUN': '1'}, text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.compose.read_bytes(), before)
        self.assertEqual(list(self.compose.parent.glob('*.pending.*')), [])

    def test_context_failure_does_not_fallback_or_mutate(self):
        before = self.observed()['calls']
        self.command('ctl.sh', 'start', 'check', extra={'ENV_TEST_FAIL_CONTEXT': '1'}, expected=1)
        self.assertTrue(all(call[0] == 'context' for call in self.observed()['calls'][len(before):]))

    def test_unconfigured_auto_context_is_rejected(self):
        manifest = self.repo / '.envstack/stack.yaml'
        manifest.write_text(manifest.read_text().replace('docker_context: fixture\n', ''))
        before = self.observed()['calls']
        self.command('ctl.sh', 'status', 'check', expected=1)
        self.assertEqual(before, self.observed()['calls'])

    def test_changed_context_cannot_operate_old_state(self):
        (self.compose.parent / 'docker-context').write_text('another-context\n')
        self.command('ctl.sh', 'start', 'check', expected=1)
        self.assertFalse(any('up' in call for call in self.observed()['calls']))

    def test_shared_infrastructure_requires_explicit_authorization(self):
        self.command('ctl.sh', 'start', 'check', extra={'ENV_ALLOW_SHARED_INFRA': '0'}, expected=1)
        self.assertFalse(any(call[0] == 'start' for call in self.observed()['calls']))

    def test_proxy_start_failure_is_not_reported_as_ready(self):
        result = self.command('ctl.sh', 'start', 'check', extra={'ENV_TEST_FAIL_PROXY': '1'}, expected=8)
        self.assertNotIn('dependencias prontos', result.stdout)
        self.assertFalse(any('up' in call for call in self.observed()['calls']))

    def test_destroy_requires_exact_confirmation(self):
        self.command('destroy.sh', 'check', '--keep-worktree', expected=1)
        self.assertTrue(self.compose.exists())
        self.assertFalse(any('down' in call for call in self.observed()['calls']))

    def test_destroy_failure_preserves_state_and_worktree(self):
        result = self.command('destroy.sh', 'check', '--confirm', 'fixture/check', '--keep-worktree', extra={'ENV_TEST_FAIL_DOWN': '1'}, expected=9)
        self.assertTrue(self.compose.exists())
        self.assertTrue(self.worktree.exists())
        self.assertNotIn('todas as etapas', result.stdout)

    def test_destroy_refuses_dirty_worktree_before_docker_mutation(self):
        self.command('destroy.sh', 'check', '--confirm', 'fixture/check', expected=1)
        self.assertTrue(self.worktree.exists())
        self.assertFalse(any('down' in call for call in self.observed()['calls']))

    def test_destroy_refuses_shared_volume(self):
        self.command('destroy.sh', 'check', '--confirm', 'fixture/check', '--keep-worktree', extra={'ENV_TEST_SHARED_VOLUME': '1'}, expected=1)
        self.assertTrue(self.compose.exists())
        self.assertFalse(any('down' in call for call in self.observed()['calls']))

    def test_destroy_keeps_requested_worktree_and_branch(self):
        self.command('destroy.sh', 'check', '--confirm', 'fixture/check', '--keep-worktree')
        self.assertFalse(self.compose.parent.exists())
        self.assertTrue(self.worktree.exists())
        self.run_process(['git', 'show-ref', '--verify', 'refs/heads/check'])

    def test_destroy_without_compose_never_guesses_by_prefix(self):
        self.compose.unlink()
        self.command('destroy.sh', 'check', '--confirm', 'fixture/check', '--keep-worktree', expected=1)
        self.assertFalse(any(call[0] in ['ps', 'rm', 'network'] for call in self.observed()['calls']))

    def test_configured_branch_base_and_ambiguous_detection(self):
        self.run_process(['git', 'branch', 'master'])
        self.command('new.sh', 'ambiguous', extra={'ENV_DRY_RUN': '1'}, expected=1)
        self.assertFalse((self.repo / '.worktrees/ambiguous').exists())
        manifest = self.repo / '.envstack/stack.yaml'
        manifest.write_text(manifest.read_text() + '\nbase_ref: main\n')
        self.command('new.sh', 'configured', extra={'ENV_DRY_RUN': '1'})
        self.assertTrue((self.repo / '.worktrees/configured').exists())

    def remove_generated_fixture_files(self):
        # Model a clean/static environment: its saved Compose needs no local env files.
        subprocess.run(['yq', '-i', 'del(.services[].env_file)', str(self.compose)], check=True)
        shutil.rmtree(self.worktree / '.idea')
        for service in ['api', 'site', 'docs']:
            (self.worktree / service / '.env').unlink()

    def test_destroy_removes_clean_integrated_worktree(self):
        self.remove_generated_fixture_files()
        self.command('destroy.sh', 'check', '--confirm', 'fixture/check')
        self.assertFalse(self.worktree.exists())
        self.assertFalse(self.compose.parent.exists())
        result = subprocess.run(['git', 'show-ref', '--verify', 'refs/heads/check'], cwd=self.repo, capture_output=True)
        self.assertNotEqual(result.returncode, 0)

    def test_destroy_preserves_unmerged_commits(self):
        self.remove_generated_fixture_files()
        (self.worktree / 'pending.txt').write_text('synthetic pending work')
        self.run_process(['git', '-C', str(self.worktree), 'add', 'pending.txt'])
        self.run_process(['git', '-C', str(self.worktree), '-c', 'user.name=Env Test', '-c', 'user.email=env@example.invalid', 'commit', '-m', 'pending'])
        self.command('destroy.sh', 'check', '--confirm', 'fixture/check', expected=1)
        self.assertTrue(self.worktree.exists())
        self.assertFalse(any('down' in call for call in self.observed()['calls']))

    def test_foreign_project_record_blocks_operations(self):
        (self.compose.parent / 'project-root').write_text('/another/project\n')
        self.command('ctl.sh', 'start', 'check', expected=1)
        self.assertFalse(any('up' in call for call in self.observed()['calls']))

    def test_engine_context_conflict_and_unknown_engine_fail(self):
        manifest = self.repo / '.envstack/stack.yaml'
        original = manifest.read_text()
        for engine in ['orbstack', 'unknown-engine']:
            manifest.write_text(original.replace('engine: auto', 'engine: ' + engine))
            self.command('ctl.sh', 'status', 'check', expected=1)

    def test_local_remote_head_selects_nonstandard_base(self):
        self.run_process(['git', 'branch', 'master'])
        self.run_process(['git', 'update-ref', 'refs/remotes/origin/stable', 'main'])
        self.run_process(['git', 'symbolic-ref', 'refs/remotes/origin/HEAD', 'refs/remotes/origin/stable'])
        self.command('new.sh', 'from-remote', extra={'ENV_DRY_RUN': '1'})
        self.assertTrue((self.repo / '.worktrees/from-remote').exists())

    def test_detect_preserves_existing_manifest(self):
        manifest = self.repo / '.envstack/stack.yaml'
        before = manifest.read_bytes()
        self.command('detect.sh', expected=1)
        self.assertEqual(before, manifest.read_bytes())

if __name__ == '__main__':
    unittest.main()
