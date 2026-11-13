"""Orquestrador do modo issue-bot com gh, tmux e env simulados; sem rede, merge ou chave de API."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

_spec = importlib.util.spec_from_file_location('issue_bot_support', Path(__file__).with_name('issue_bot_support.py'))
support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(support)
ROOT = support.ROOT
SKILL = support.SKILL
check = support.check

ISSUE_BODY = '''Filtrar a lista por período.

## Critérios de aceite
- AC-01: O usuário consegue filtrar a lista por período.
- AC-02: Somente o próprio tenant vê os registros.

## Fora de escopo
- Relatórios.
'''

FAKE_ENV_CTL = r'''#!/usr/bin/env bash
state="$FAKE_ENV_DIR"
echo "$* allow=${ENV_ALLOW_SHARED_INFRA:-0}" >> "$state/calls.log"
case "$1" in
  status) cat "$state/status.json"; [ -f "$state/ready" ] && exit 0 || exit 5 ;;
  ensure) [ "${ENV_ALLOW_SHARED_INFRA:-0}" = 1 ] || exit 1; touch "$state/ready"; exit 0 ;;
esac
exit 1
'''


def example(name):
    return json.loads((SKILL / 'references' / name).read_text())


def approved(doc):
    doc = copy.deepcopy(doc)
    doc['veredito'] = 'pode_mergear'
    doc['ajustes'] = [a for a in doc['ajustes'] if a['gravidade'] == 'sugestao']
    for criterion in doc['criterios']:
        criterion['status'] = 'atendido'
    return doc


class IssueBotTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='issue-bot-')
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.project = self.base / 'rcastello'
        (self.project / '.bezalel').mkdir(parents=True)
        subprocess.run(['git', 'init', '-q', '-b', 'main'], cwd=self.project, check=True)
        (self.project / '.bezalel/.gitignore').write_text('/handoff/\n/logs/\n')
        self.config = json.loads((ROOT / 'agents/templates/project.example.json').read_text())
        self.config['project'] = 'RCastello'
        self.save_config()
        self.handoffs = self.project / '.bezalel/handoff'
        self.claude = example('handoff-claude.example.json')
        self.codex = example('handoff-codex.example.json')
        window = {'cwd': str(self.project), 'pane': [], 'pipe': 'cat'}
        self.env = support.fake_environment(self.base, gh_state={
            'checks': [check('tests', 'pass')], 'sha': 'abc123def',
            'issue': {'number': 122, 'title': 'Filtro por período', 'body': ISSUE_BODY,
                      'url': 'https://github.com/exemplo/rcastello/issues/122'},
            'prs': [{'number': 130, 'headRefName': 'issue-122', 'closingIssuesReferences': [{'number': 122}]}],
        }, tmux_state={'sessions': {'rcastello-122': {'options': {}, 'windows': {
            'codex': {**window, 'command': 'codex'}, 'claude': {**window, 'command': 'claude'}}}}})
        self.env.pop('ENV_ALLOW_SHARED_INFRA', None)

    def save_config(self):
        (self.project / '.bezalel/project.json').write_text(json.dumps(self.config))

    def write(self, name, doc):
        self.handoffs.mkdir(parents=True, exist_ok=True)
        (self.handoffs / name).write_text(json.dumps(doc))

    def bot(self, *args, expected=0, script=None):
        command = [sys.executable, '-B', str(script or SKILL / 'scripts/issue_bot.py'), *args,
                   '--project', str(self.project), '--issue', '122', '--wait-seconds', '0', '--ci-timeout-seconds', '0']
        if args[0] in {'session-up', 'session-down', 'prepare-prompt', 'status', 'env-up', 'implement'}:
            command = command[:-4]
        result = subprocess.run(command, capture_output=True, text=True, env=self.env)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        self.assertFalse(any(c[:2] in (['pr', 'merge'], ['pr', 'review']) for c in self.gh_calls()))
        return result

    def gh_calls(self):
        return json.loads((self.base / 'gh.json').read_text())['calls']

    def tmux(self):
        return json.loads((self.base / 'tmux.json').read_text())

    def set_tmux(self, **changes):
        state = self.tmux()
        state.update(changes)
        (self.base / 'tmux.json').write_text(json.dumps(state))

    def set_gh(self, **changes):
        state = json.loads((self.base / 'gh.json').read_text())
        state.update(changes)
        (self.base / 'gh.json').write_text(json.dumps(state))

    def pasted(self, window):
        return [c for c in self.tmux()['calls'] if c[0] == 'paste-buffer' and c[-1].endswith(':' + window)]

    def test_root_wrapper_help_lists_all_commands(self):
        result = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/issue_bot.py'), '--help'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        for name in ['session-up', 'session-down', 'implement', 'ci-gate', 'review', 'respond', 'env-up', 'status', 'prepare-prompt']:
            self.assertIn(name, result.stdout)
        self.assertIn('Nenhum código autoriza merge', result.stdout)

    def test_prepare_prompt_substitutes_placeholders_and_rules(self):
        for kind in ['implement', 'review', 'respond', 'corrigir-ci', 'subir-ambiente']:
            with self.subTest(kind=kind):
                if kind == 'respond':
                    self.write('122-r1-claude.json', self.claude)
                text = self.bot('prepare-prompt', kind).stdout
                self.assertNotIn('{{', text)
                self.assertIn(str(self.project), text)
                self.assertIn('merge', text)
                self.assertIn('chave de API', text)
                self.assertIn('crit', text.lower())
        review = self.bot('prepare-prompt', 'review').stdout
        self.assertIn('AC-02: Somente o próprio tenant', review)
        self.assertNotIn('Relatórios.\n\n## Fora', review.split('Critérios de aceite extraídos da issue:')[1].split('Conteúdo da issue')[0])
        self.assertIn('.bezalel/handoff/122-r2-claude.json', review)
        self.assertIn('gh pr diff 130', review)
        self.assertIn('pr-audit', review)
        implement = self.bot('prepare-prompt', 'implement').stdout
        self.assertIn('Closes #122', implement)
        self.assertIn('.worktrees/issue-122', implement)
        self.assertIn('Não gere roteiro Excel', implement)
        self.assertIn('migration', implement)

    def test_issue_without_criteria_is_not_invented(self):
        self.set_gh(issue={'number': 122, 'title': 'x', 'body': 'Sem seção.', 'url': 'https://github.com/e/r/issues/122'})
        self.assertIn('Não invente critérios', self.bot('prepare-prompt', 'implement').stdout)

    def test_review_refuses_without_green_ci(self):
        for bucket, code in [('fail', 2), ('pending', 3)]:
            with self.subTest(bucket=bucket):
                self.set_gh(checks=[check('tests', bucket)])
                self.bot('review', expected=code)
                self.assertEqual(self.pasted('claude'), [])
        self.set_gh(checks=[])
        self.bot('review', expected=3)

    def test_review_sends_prompt_and_validates_handoff(self):
        target = self.handoffs / '122-r1-claude.json'
        self.set_tmux(on_paste={'claude': {'path': str(target), 'content': json.dumps(self.claude)}})
        result = self.bot('review', expected=2)
        summary = json.loads(result.stdout)
        self.assertEqual((summary['veredito'], summary['rodada'], summary['bloqueantes_abertos']), ('ajustes', 1, 1))
        self.assertFalse(summary['merge_autorizado'])
        self.assertEqual(len(self.pasted('claude')), 1)
        # Reexecutar não envia nova revisão enquanto o Codex não responder.
        self.bot('review', expected=2)
        self.assertEqual(len(self.pasted('claude')), 1)

    def test_invalid_handoff_does_not_advance(self):
        bad = {**self.claude, 'ci': {'status': 'pending', 'evidence': 'x'}}
        self.set_tmux(on_paste={'claude': {'path': str(self.handoffs / '122-r1-claude.json'), 'content': json.dumps(bad)}})
        self.assertIn('inválido', self.bot('review', expected=1).stderr)

    def test_mergeable_review_exits_zero_without_merge(self):
        self.set_tmux(on_paste={'claude': {'path': str(self.handoffs / '122-r1-claude.json'), 'content': json.dumps(approved(self.claude))}})
        summary = json.loads(self.bot('review').stdout)
        self.assertTrue(summary['pronto_para_humano'])
        self.assertFalse(summary['merge_autorizado'])

    def test_respond_then_round_two_then_limit(self):
        self.write('122-r1-claude.json', self.claude)
        self.set_tmux(on_paste={'codex': {'path': str(self.handoffs / '122-r1-codex.json'), 'content': json.dumps(self.codex)}})
        self.assertTrue(json.loads(self.bot('respond').stdout)['resposta_codex'])
        self.assertEqual(len(self.pasted('codex')), 1)
        second = {**self.claude, 'rodada': 2}
        self.set_tmux(on_paste={'claude': {'path': str(self.handoffs / '122-r2-claude.json'), 'content': json.dumps(second)}})
        self.assertEqual(json.loads(self.bot('review', expected=2).stdout)['rodada'], 2)
        self.assertIn('122-r1-codex.json', self.pasted_text('claude'))
        # Depois de duas rodadas com ajustes, nem resposta nem revisão sem decisão humana.
        self.bot('respond', expected=4)
        self.write('122-r2-codex.json', {**self.codex, 'rodada': 2})
        before = len(self.pasted('claude'))
        self.assertIn('decisão humana', self.bot('review', expected=4).stdout)
        self.assertEqual(len(self.pasted('claude')), before)
        self.write('122-decisao.json', {**example('decisao.example.json'), 'autorizado_ate': 3})
        self.set_tmux(on_paste={'claude': {'path': str(self.handoffs / '122-r3-claude.json'), 'content': json.dumps(approved({**self.claude, 'rodada': 3}))}})
        self.assertEqual(json.loads(self.bot('review').stdout)['rodada'], 3)

    def pasted_text(self, window):
        return '\n'.join(w for w in self.tmux()['sessions']['rcastello-122']['windows'][window]['pane'])

    def test_dry_run_prints_prompt_without_tmux_keys(self):
        result = self.bot('review', '--dry-run')
        self.assertIn('rodada 1', result.stdout)
        self.assertFalse(any(c[0] in ('paste-buffer', 'send-keys', 'load-buffer') for c in self.tmux()['calls']))
        self.bot('implement', '--dry-run')
        self.assertFalse(any(c[0] in ('paste-buffer', 'send-keys') for c in self.tmux()['calls']))

    def test_ci_gate_sends_fix_only_when_red(self):
        self.bot('ci-gate', '--send-fix')
        self.assertEqual(self.pasted('codex'), [])
        self.set_gh(checks=[check('tests', 'fail')])
        result = self.bot('ci-gate', '--send-fix', expected=2)
        self.assertEqual(json.loads(result.stdout.split('\n}\n')[0] + '\n}')['status'], 'failed')
        self.assertEqual(len(self.pasted('codex')), 1)
        self.assertIn('não conta como rodada', self.pasted_text('codex'))

    def test_status_reports_stable_json(self):
        self.write('122-r1-claude.json', self.claude)
        status = json.loads(self.bot('status', '--offline').stdout)
        for key in ['issue', 'pr', 'ciclo', 'rodada', 'ci', 'veredito', 'handoff', 'sessao', 'ambiente', 'merge_autorizado']:
            self.assertIn(key, status)
        self.assertEqual((status['pr'], status['rodada'], status['veredito']), (130, 1, 'ajustes'))
        self.assertEqual(status['handoff']['claude'], '.bezalel/handoff/122-r1-claude.json')
        online = json.loads(self.bot('status').stdout)
        self.assertEqual(online['ci']['status'], 'passed')
        self.assertTrue(online['sessao']['exists'])

    def test_handoff_folder_must_be_ignored(self):
        (self.project / '.bezalel/.gitignore').write_text('')
        self.assertIn('/handoff/', self.bot('review', expected=1).stderr)
        self.bot('session-up', '--dry-run', expected=1)

    def env_fixture(self):
        skill = self.base / 'env-skill'
        support.install(skill / 'scripts', 'ctl.sh', FAKE_ENV_CTL)
        state = self.base / 'env-state'
        state.mkdir()
        worktree = self.project / '.worktrees/issue-122'
        (worktree / 'api').mkdir(parents=True)
        (state / 'status.json').write_text(json.dumps({'environment': 'issue-122', 'worktree': str(worktree), 'services': []}))
        self.env['FAKE_ENV_DIR'] = str(state)
        self.write('122-r1-claude.json', approved(self.claude))
        return ['--env-skill-dir', str(skill)], state, worktree

    def test_env_up_asks_for_infra_and_data_decisions(self):
        extra, state, _ = self.env_fixture()
        self.bot('env-up', *extra, expected=5)
        self.assertNotIn('ensure', (state / 'calls.log').read_text())
        result = self.bot('env-up', *extra, '--allow-shared-infra', expected=5)
        self.assertEqual(json.loads(result.stdout)['decisao_pendente'], 'dados')
        self.assertIn('ensure issue-122 --issue 122 allow=1', (state / 'calls.log').read_text())
        self.assertTrue(all(line.endswith('allow=0') for line in (state / 'calls.log').read_text().splitlines() if line.startswith('status')))
        self.assertEqual(json.loads(self.bot('env-up', *extra, '--data-mode', 'empty').stdout)['dados']['restaurado'], False)
        self.config['data'] = {'mode': 'empty'}
        self.save_config()
        self.bot('env-up', *extra)

    def test_env_up_restores_snapshot_after_ready_once(self):
        extra, state, worktree = self.env_fixture()
        (state / 'ready').touch()
        flag = worktree / 'api/restored.flag'
        self.config['data'] = {'mode': 'snapshot', 'dataset': 'tiny', 'workdir': 'api',
                               'restore': [sys.executable, '-c', "open('restored.flag','w').write('ok')"]}
        self.save_config()
        result = json.loads(self.bot('env-up', *extra).stdout)
        self.assertTrue(result['dados']['restaurado'])
        self.assertEqual(flag.read_text(), 'ok')
        flag.unlink()
        self.bot('env-up', *extra)
        self.assertFalse(flag.exists())
        self.bot('env-up', *extra, '--restore-again')
        self.assertTrue(flag.exists())
        self.config['data']['restore'] = [sys.executable, '-c', 'raise SystemExit(7)']
        self.save_config()
        result = json.loads(self.bot('env-up', *extra, '--restore-again', expected=1).stdout)
        self.assertEqual(result['dados']['codigo_saida'], 7)

    def test_env_up_requires_finished_review(self):
        extra, _, _ = self.env_fixture()
        (self.handoffs / '122-r1-claude.json').write_text(json.dumps(self.claude))
        self.bot('env-up', *extra, expected=1)
        self.config['schema_version'] = 2
        self.save_config()
        self.bot('env-up', *extra, '--allow-before-review', expected=5)


if __name__ == '__main__':
    unittest.main()
