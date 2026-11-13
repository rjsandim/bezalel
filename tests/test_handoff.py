"""Contrato de handoff do modo issue-bot, com fixtures sintéticas e sem rede."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/issue-bot'
spec = importlib.util.spec_from_file_location('check_handoff', SKILL / 'scripts/check_handoff.py')
handoff = importlib.util.module_from_spec(spec)
spec.loader.exec_module(handoff)


def example(name):
    return json.loads((SKILL / 'references' / name).read_text())


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='handoff-')
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name)
        self.dir = self.project / '.bezalel/handoff'
        self.dir.mkdir(parents=True)
        self.claude = example('handoff-claude.example.json')
        self.codex = example('handoff-codex.example.json')

    def write(self, name, value):
        (self.dir / name).write_text(json.dumps(value) if not isinstance(value, str) else value)

    def approve(self, doc):
        doc = copy.deepcopy(doc)
        doc['veredito'] = 'pode_mergear'
        doc['ajustes'] = [a for a in doc['ajustes'] if a['gravidade'] == 'sugestao']
        for criterion in doc['criterios']:
            criterion['status'] = 'atendido'
        return doc

    def validate(self, **kw):
        return handoff.validate_round(self.project, 122, **kw)

    def assertInvalid(self, fragment=None, **kw):
        with self.assertRaises(handoff.HandoffError) as caught:
            self.validate(**kw)
        if fragment:
            self.assertIn(fragment, str(caught.exception))

    def test_official_examples_pass_as_pair(self):
        self.write('122-r1-claude.json', self.claude)
        self.write('122-r1-codex.json', self.codex)
        summary = self.validate()
        self.assertEqual(summary['veredito'], 'ajustes')
        self.assertEqual(summary['bloqueantes_abertos'], 0)
        self.assertTrue(summary['resposta_codex'])
        self.assertFalse(summary['pronto_para_humano'])
        self.assertFalse(summary['merge_autorizado'])
        self.write('122-decisao.json', example('decisao.example.json'))
        self.assertEqual(self.validate()['limite_rodadas'], 4)

    def test_claude_alone_reports_open_blockers(self):
        self.write('122-r1-claude.json', self.claude)
        summary = self.validate()
        self.assertEqual(summary['bloqueantes_abertos'], 1)
        self.assertEqual(summary['criterios_pendentes'], 1)
        self.assertFalse(summary['resposta_codex'])
        self.assertInvalid('Codex ausente', role='codex')

    def test_mergeable_with_only_suggestions_is_valid_but_not_merge(self):
        self.write('122-r1-claude.json', self.approve(self.claude))
        summary = self.validate()
        self.assertEqual(summary['veredito'], 'pode_mergear')
        self.assertTrue(summary['pronto_para_humano'])
        self.assertFalse(summary['merge_autorizado'])

    def test_mergeable_rejects_blocker_or_unmet_criterion(self):
        doc = self.approve(self.claude)
        doc['ajustes'].append({**self.claude['ajustes'][0]})
        self.write('122-r1-claude.json', doc)
        self.assertInvalid('pode_mergear')
        doc = self.approve(self.claude)
        doc['criterios'][0]['status'] = 'nao_atendido'
        self.write('122-r1-claude.json', doc)
        self.assertInvalid('pode_mergear')

    def test_adjustments_need_blocker_or_pending_criterion(self):
        doc = self.approve(self.claude)
        doc['veredito'] = 'ajustes'
        self.write('122-r1-claude.json', doc)
        self.assertInvalid('ajustes exige')

    def test_review_requires_green_ci(self):
        for status in ['pending', 'failed', 'not_applicable']:
            with self.subTest(status=status):
                doc = copy.deepcopy(self.claude)
                doc['ci']['status'] = status
                self.write('122-r1-claude.json', doc)
                self.assertInvalid('CI verde')

    def test_codex_unknown_adjustment_and_missing_blocker(self):
        self.write('122-r1-claude.json', self.claude)
        doc = copy.deepcopy(self.codex)
        doc['ajustes'].append({'id': 'A9', 'status': 'corrigido', 'como': 'x', 'commit': 'abcdef1'})
        self.write('122-r1-codex.json', doc)
        self.assertInvalid('A9')
        doc = copy.deepcopy(self.codex)
        doc['ajustes'] = [a for a in doc['ajustes'] if a['id'] != 'A1']
        self.write('122-r1-codex.json', doc)
        self.assertInvalid('bloqueantes')
        doc = copy.deepcopy(self.codex)
        doc['ajustes'][0]['commit'] = None
        self.write('122-r1-codex.json', doc)
        self.assertInvalid('SHA')

    def test_codex_must_match_claude_pr_and_not_answer_mergeable(self):
        self.write('122-r1-claude.json', self.claude)
        self.write('122-r1-codex.json', {**self.codex, 'pr': 131})
        self.assertInvalid('PR diverge')
        self.write('122-r1-claude.json', self.approve(self.claude))
        self.write('122-r1-codex.json', self.codex)
        self.assertInvalid('pode_mergear')

    def test_round_three_requires_iterate_decision(self):
        for rnd in (1, 2):
            self.write(f'122-r{rnd}-claude.json', {**self.claude, 'rodada': rnd})
            self.write(f'122-r{rnd}-codex.json', {**self.codex, 'rodada': rnd})
        self.write('122-r3-claude.json', {**self.claude, 'rodada': 3})
        self.assertInvalid('decisão humana iterar')
        decision = example('decisao.example.json')
        self.write('122-decisao.json', {**decision, 'decisao': 'finalizar', 'autorizado_ate': None})
        self.assertInvalid('decisão humana iterar')
        self.write('122-decisao.json', {**decision, 'autorizado_ate': 3})
        self.assertEqual(self.validate()['rodada'], 3)
        self.write('122-decisao.json', {**decision, 'autorizado_ate': 2})
        self.assertInvalid('autorizado_ate')

    def test_later_round_requires_previous_codex_answer(self):
        self.write('122-r1-claude.json', self.claude)
        self.write('122-r2-claude.json', {**self.claude, 'rodada': 2})
        self.assertInvalid('resposta do Codex da rodada 1')

    def test_file_name_must_match_fields_and_unknown_root_fields(self):
        self.write('122-r1-claude.json', {**self.claude, 'rodada': 2})
        self.assertInvalid('nome do arquivo')
        self.write('122-r1-claude.json', {**self.claude, 'papel': 'codex'})
        self.assertInvalid('papel')
        self.write('122-r1-claude.json', {**self.claude, 'merge': True})
        self.assertInvalid('campos desconhecidos')
        self.write('122-r1-claude.json', '{"schema_version": 1,')
        self.assertInvalid('malformado')

    def test_cycle_patterns_and_collision(self):
        self.write('122-r1-claude.json', self.approve(self.claude))
        self.write('122-c2-r1-claude.json', {**self.claude, 'ciclo': 2})
        summary = self.validate()
        self.assertEqual((summary['ciclo'], summary['rodada']), (2, 1))
        self.assertEqual(self.validate(cycle=1)['veredito'], 'pode_mergear')
        self.write('122-c2-r1-codex.json', self.codex)
        self.assertInvalid('ciclo', cycle=2, role='par')
        self.write('122-c1-r1-claude.json', self.claude)
        self.assertInvalid('Colisão')

    def test_cli_prints_summary_and_fixed_diagnostics(self):
        self.write('122-r1-claude.json', self.claude)
        script = SKILL / 'scripts/check_handoff.py'
        result = subprocess.run([sys.executable, '-B', str(script), '--project', str(self.project), '--issue', '122'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['veredito'], 'ajustes')
        self.write('122-r1-claude.json', {**self.claude, 'segredo': 'valor-privado'})
        result = subprocess.run([sys.executable, '-B', str(script), '--project', str(self.project), '--issue', '122'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertNotIn('valor-privado', result.stderr)

    def test_repository_checker_requires_issue_bot_files_prompts_and_links(self):
        sys.path.insert(0, str(ROOT / 'scripts'))
        import check_repository
        self.assertEqual(check_repository.validate_issue_bot(), [])
        copy_root = self.project / 'arvore'
        for name in check_repository.ISSUE_BOT_FILES + ['README.md', 'agents/README.md', 'agents/dream-team.md'] + [
                'skills/issue-bot/prompts/' + p + '.md' for p in check_repository.ISSUE_BOT_PROMPTS]:
            target = copy_root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / name).read_bytes())
        original = check_repository.ROOT
        try:
            check_repository.ROOT = copy_root
            self.assertEqual(check_repository.validate_issue_bot(), [])
            (copy_root / 'agents/issue-bot.md').unlink()
            (copy_root / 'skills/issue-bot/prompts/revisar.md').unlink()
            prompt = copy_root / 'skills/issue-bot/prompts/implementar.md'
            prompt.write_text(prompt.read_text().replace('chave de API', 'credencial'))
            readme = copy_root / 'README.md'
            readme.write_text(readme.read_text().replace('](agents/issue-bot.md', '](agents/outro.md'))
            errors = '\n'.join(check_repository.validate_issue_bot())
        finally:
            check_repository.ROOT = original
        for fragment in ['agents/issue-bot.md', 'prompt ausente: revisar', "implementar sem a regra obrigatória 'chave de API'", 'README.md precisa']:
            self.assertIn(fragment, errors)

    def test_schema_documents_both_roles_and_decision(self):
        schema = json.loads((SKILL / 'references/handoff.schema.json').read_text())
        self.assertEqual(schema['$schema'], 'https://json-schema.org/draft/2020-12/schema')
        self.assertEqual(set(schema['$defs']['claude']['properties']), handoff.CLAUDE_FIELDS)
        self.assertEqual(set(schema['$defs']['codex']['properties']), handoff.CODEX_FIELDS)
        self.assertEqual(set(schema['$defs']['decisao']['properties']), handoff.DECISION_FIELDS)


if __name__ == '__main__':
    unittest.main()
