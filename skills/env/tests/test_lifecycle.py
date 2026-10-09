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
    sys.exit(0)
if args[0] == 'start':
    sys.exit(0)
if args[0] != 'compose':
    sys.exit('Unexpected Docker operation: ' + repr(args))
file = args[2]
command = args[3]
rest = args[4:]
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
        self.run_process(['git', 'init', '-b', 'master'])
        self.run_process(['git', 'add', '.'])
        self.run_process(['git', '-c', 'user.name=Env Test', '-c', 'user.email=env@example.invalid', '-c', 'core.hooksPath=/dev/null', 'commit', '-m', 'fixture'])
        self.state = self.base / 'docker-state.json'
        self.state.write_text(json.dumps({'running': [], 'ids': {}, 'calls': []}))
        bindir = self.base / 'bin'
        bindir.mkdir()
        (bindir / 'docker').write_text(FAKE_DOCKER)
        (bindir / 'docker').chmod(0o755)
        self.env = {**os.environ, 'PATH': str(bindir) + os.pathsep + os.environ['PATH'], 'ENV_TEST_STATE': str(self.state), 'ENV_TEST_DOCKER': DOCKER}
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

if __name__ == '__main__':
    unittest.main()
