"""Sessão tmux do modo issue-bot com tmux e CLIs simulados; nada anexa ao terminal do operador."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import unittest

_spec = importlib.util.spec_from_file_location('issue_bot_support', Path(__file__).with_name('issue_bot_support.py'))
support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(support)
SCRIPT = support.SKILL / 'scripts/issue_session.sh'

FAKE_CLI = r'''#!/bin/sh
# Dublê de codex/claude: só responde ao status de login; o modo interativo fica parado.
case "$FAKE_LOGIN" in
  account) codex_out='Logged in using ChatGPT'; claude_out='{"loggedIn": true, "authMethod": "claude.ai"}' ;;
  apikey) codex_out='Logged in using an API key - sk-PRIVATE'; claude_out='{"loggedIn": true, "authMethod": "api_key"}' ;;
  *) exit 1 ;;
esac
if [ "$1 $2" = "login status" ]; then echo "$codex_out"; exit 0; fi
if [ "$1 $2" = "auth status" ]; then echo "$claude_out"; exit 0; fi
[ -z "$OPENAI_API_KEY$ANTHROPIC_API_KEY" ] || { echo "chave de API vazou" >&2; exit 42; }
exec cat
'''


def git(cwd, *args):
    subprocess.run(['git', *args], cwd=cwd, check=True, capture_output=True)


class IssueSessionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='issue-session-')
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.project = self.base / 'rcastello'
        self.project.mkdir()
        git(self.project, 'init', '-q', '-b', 'main')
        self.env = support.fake_environment(self.base, tmux_state={})
        for name in ('codex', 'claude'):
            support.install(self.base / 'bin', name, FAKE_CLI)
        self.env.update({'FAKE_LOGIN': 'account', 'OPENAI_API_KEY': 'sk-fixture', 'ANTHROPIC_API_KEY': 'sk-ant-fixture'})

    def run_script(self, *args, expected=0, env=None):
        result = subprocess.run(['bash', str(SCRIPT), *args], capture_output=True, text=True, env=env or self.env)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def tmux(self):
        return json.loads((self.base / 'tmux.json').read_text())

    def create(self, **extra):
        args = ['create', '--project-name', 'RCastello', '--issue', '122', '--cwd', str(self.project)]
        return self.run_script(*args, **extra)

    def test_create_opens_two_windows_with_logs_and_hint(self):
        result = self.create()
        self.assertIn('tmux attach -t rcastello-122', result.stdout)
        session = self.tmux()['sessions']['rcastello-122']
        self.assertEqual(list(session['windows']), ['codex', 'claude'])
        logs = self.project / '.bezalel/logs'
        for name, window in session['windows'].items():
            self.assertEqual(window['cwd'], str(self.project))
            self.assertIn(str(logs / f'rcastello-122-{name}.log'), window['pipe'])
            self.assertEqual(window['command'], name)
        launches = [c for c in self.tmux()['calls'] if c[0] == 'send-keys' and '-l' in c]
        self.assertTrue(any('codex' in c[-1] and 'workspace-write' in c[-1] and '-u OPENAI_API_KEY' in c[-1] for c in launches))
        self.assertTrue(any('claude' in c[-1] and '--dangerously-skip-permissions' in c[-1] for c in launches))
        self.assertNotIn('sk-fixture', json.dumps(self.tmux()))
        self.assertTrue(logs.is_dir())

    def test_create_is_idempotent_and_keeps_logs_and_clis(self):
        self.create()
        log = self.project / '.bezalel/logs/rcastello-122-codex.log'
        log.write_text('trabalho anterior\n')
        before = len([c for c in self.tmux()['calls'] if c[0] in ('new-session', 'send-keys')])
        self.create()
        calls = self.tmux()['calls']
        self.assertEqual(len([c for c in calls if c[0] in ('new-session', 'send-keys')]), before)
        self.assertFalse(any(c[0] == 'kill-session' for c in calls))
        self.assertTrue(all('-o' in c for c in calls if c[0] == 'pipe-pane'))
        self.assertEqual(log.read_text(), 'trabalho anterior\n')

    def test_invalid_names_and_cwd_are_refused(self):
        for name, issue in [('codex/foo', '122'), ('RCastello - #', '122'), ('rcastello', '0'), ('rcastello', 'abc')]:
            with self.subTest(name=name, issue=issue):
                self.run_script('create', '--project-name', name, '--issue', issue, '--cwd', str(self.project), expected=1)
        sub = self.project / 'api'
        sub.mkdir()
        self.run_script('create', '--project-name', 'rcastello', '--issue', '122', '--cwd', str(sub), expected=1)
        self.assertEqual(self.tmux()['sessions'], {})
        self.run_script('send', '--session', 'Rcastello-122', '--window', 'codex', '--text-file', '/dev/null', expected=1)

    def test_api_key_login_or_missing_login_is_refused(self):
        for login in ('apikey', 'none'):
            with self.subTest(login=login):
                result = self.create(env={**self.env, 'FAKE_LOGIN': login}, expected=1)
                self.assertNotIn('PRIVATE', result.stderr)
                self.assertIn('login', result.stderr)
                self.assertFalse(any(c[0] == 'send-keys' for c in self.tmux()['calls']))

    def test_send_capture_status_and_destroy(self):
        self.create()
        prompt = self.base / 'prompt.md'
        prompt.write_text('Implemente a issue 122.\nSegunda linha.\n')
        self.run_script('send', '--session', 'rcastello-122', '--window', 'codex', '--text-file', str(prompt))
        captured = self.run_script('capture', '--session', 'rcastello-122', '--window', 'codex').stdout
        self.assertIn('Implemente a issue 122.\nSegunda linha.', captured)
        self.assertTrue(any(c[0] == 'paste-buffer' and '-p' in c for c in self.tmux()['calls']))
        status = json.loads(self.run_script('status', '--session', 'rcastello-122').stdout)
        self.assertTrue(status['exists'])
        self.assertEqual([w['name'] for w in status['windows']], ['codex', 'claude'])
        self.assertTrue(all(w['cli_alive'] for w in status['windows']))
        self.assertEqual(status['attach'], 'tmux attach -t rcastello-122')
        log = self.project / '.bezalel/logs/rcastello-122-claude.log'
        log.write_text('linha registrada\n')
        self.assertIn('linha registrada', self.run_script('logs', '--session', 'rcastello-122', '--window', 'claude').stdout)
        self.run_script('destroy', '--session', 'rcastello-122')
        self.assertNotIn('rcastello-122', self.tmux()['sessions'])
        self.assertTrue(log.is_file())
        self.assertFalse(json.loads(self.run_script('status', '--session', 'rcastello-122').stdout)['exists'])
        self.run_script('logs', '--session', 'rcastello-122', '--window', 'claude', '--log-dir', str(log.parent))

    def test_send_refuses_dead_window_and_binary_file(self):
        self.create()
        state = self.tmux()
        state['sessions']['rcastello-122']['windows']['claude']['command'] = 'zsh'
        (self.base / 'tmux.json').write_text(json.dumps(state))
        prompt = self.base / 'prompt.md'
        prompt.write_text('texto\n')
        self.run_script('send', '--session', 'rcastello-122', '--window', 'claude', '--text-file', str(prompt), expected=1)
        prompt.write_bytes(b'a\x00b')
        self.run_script('send', '--session', 'rcastello-122', '--window', 'codex', '--text-file', str(prompt), expected=1)

    def test_hint_is_exact(self):
        hint = self.run_script('hint', '--session', 'rcastello-122').stdout.splitlines()
        self.assertEqual(hint[0], 'tmux attach -t rcastello-122')


@unittest.skipUnless(os.environ.get('ISSUE_BOT_TMUX_SMOKE') == '1' and shutil.which('tmux'),
                     'Fumaça com tmux real: defina ISSUE_BOT_TMUX_SMOKE=1 (servidor isolado, CLIs simulados).')
class IssueSessionSmoke(unittest.TestCase):
    def test_real_tmux_round_trip(self):
        with tempfile.TemporaryDirectory(prefix='issue-smoke-') as tmp:
            base = Path(tmp).resolve()
            project = base / 'fumaca'
            project.mkdir()
            git(project, 'init', '-q', '-b', 'main')
            for name in ('codex', 'claude'):
                support.install(base / 'bin', name, FAKE_CLI)
            env = {k: v for k, v in os.environ.items() if k != 'TMUX'}
            env.update({'PATH': str(base / 'bin') + os.pathsep + env['PATH'], 'TMUX_TMPDIR': str(base), 'FAKE_LOGIN': 'account'})
            run = lambda *a: subprocess.run(['bash', str(SCRIPT), *a], capture_output=True, text=True, env=env)
            try:
                self.assertEqual(run('create', '--project-name', 'fumaca', '--issue', '1', '--cwd', str(project)).returncode, 0)
                time.sleep(1)
                prompt = base / 'prompt.md'
                prompt.write_text('ola-fumaca\n')
                self.assertEqual(run('send', '--session', 'fumaca-1', '--window', 'codex', '--text-file', str(prompt)).returncode, 0)
                time.sleep(1)
                self.assertIn('ola-fumaca', run('capture', '--session', 'fumaca-1', '--window', 'codex').stdout)
            finally:
                run('destroy', '--session', 'fumaca-1')


if __name__ == '__main__':
    unittest.main()
