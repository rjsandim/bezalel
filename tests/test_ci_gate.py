"""Portão de CI com `gh` simulado: verde, vermelho, pendente e misturas, sem rede."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

_spec = importlib.util.spec_from_file_location('issue_bot_support', Path(__file__).with_name('issue_bot_support.py'))
support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(support)
ci_gate = support.load('ci_gate')
check = support.check


class CiGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='ci-gate-')
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.project = self.base / 'project'
        self.project.mkdir()

    def run_gate(self, gh_state, *extra):
        env = support.fake_environment(self.base, gh_state=gh_state)
        result = subprocess.run([sys.executable, '-B', str(support.SKILL / 'scripts/ci_gate.py'), '--project', str(self.project),
                                 '--pr', '130', *extra], capture_output=True, text=True, env=env)
        calls = json.loads((self.base / 'gh.json').read_text())['calls']
        self.assertFalse(any(c[:2] == ['pr', 'merge'] for c in calls))
        return result

    def test_all_green_exits_zero(self):
        result = self.run_gate({'checks': [check('tests', 'pass'), check('lint', 'skipping')]}, '--timeout-seconds', '0')
        self.assertEqual(result.returncode, 0, result.stderr)
        state = json.loads(result.stdout)
        self.assertEqual(state['status'], 'passed')
        self.assertEqual(state['scope'], 'all')
        self.assertEqual(state['sha'], 'abc1234')
        self.assertFalse(state['merge_autorizado'])
        self.assertIn('gh pr checks em', state['evidence'])

    def test_failed_or_cancelled_check_exits_two_and_lists_it(self):
        for bucket in ['fail', 'cancel']:
            with self.subTest(bucket=bucket):
                result = self.run_gate({'checks': [check('tests', bucket), check('lint', 'pending')]}, '--timeout-seconds', '0')
                self.assertEqual(result.returncode, 2)
                state = json.loads(result.stdout)
                self.assertEqual(state['status'], 'failed')
                self.assertIn({'name': 'tests', 'status': 'failed', 'url': 'https://github.com/exemplo/projeto/actions/runs/1'}, state['checks'])

    def test_pending_with_zero_timeout_or_dry_run_exits_three(self):
        for extra in (['--timeout-seconds', '0'], ['--dry-run']):
            with self.subTest(extra=extra):
                result = self.run_gate({'checks': [check('tests', 'pass'), check('e2e', 'pending')]}, *extra)
                self.assertEqual(result.returncode, 3)
                self.assertEqual(json.loads(result.stdout)['status'], 'pending')

    def test_no_reported_checks_never_passes(self):
        result = self.run_gate({'checks': []}, '--dry-run')
        self.assertEqual(result.returncode, 3)
        self.assertEqual(json.loads(result.stdout)['checks'], [])

    def test_required_checks_take_precedence_when_github_distinguishes(self):
        result = self.run_gate({'checks': [check('tests', 'pass'), check('optional', 'fail')],
                                'required': [check('tests', 'pass')]}, '--dry-run')
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(json.loads(result.stdout)['scope'], 'required')

    def test_polls_until_green_without_real_sleep(self):
        env = support.fake_environment(self.base, gh_state={'checks_sequence': [
            [check('tests', 'pending')], [check('tests', 'pending')], [check('tests', 'pass')]]})
        sleeps = []
        clock = iter(range(0, 1000, 10))
        with mock.patch.dict(os.environ, env, clear=True):
            code, state = ci_gate.gate(self.project, 130, timeout=600, poll=30, sleep=sleeps.append, clock=lambda: next(clock))
        self.assertEqual((code, state['status']), (0, 'passed'))
        self.assertEqual(len(sleeps), 2)

    def test_tool_failure_is_usage_error(self):
        env = support.fake_environment(self.base, gh_state={'checks': []})
        env['PATH'] = str(self.base / 'empty') + os.pathsep + '/usr/bin:/bin'
        result = subprocess.run([sys.executable, '-B', str(support.SKILL / 'scripts/ci_gate.py'), '--project', str(self.project),
                                 '--pr', '130', '--dry-run'], capture_output=True, text=True, env=env)
        self.assertEqual(result.returncode, 1)
        self.assertIn('gh', result.stderr)


if __name__ == '__main__':
    unittest.main()
