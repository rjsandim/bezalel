"""Contratos sintéticos; decisões de fixture não autorizam execução real."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import check_handoff as h
from check_delivery import ContractError


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.project=Path(self.tmp.name).resolve()
        self.directory=self.project/'.bezalel/handoff'
        self.directory.mkdir(parents=True)
        self.claude=json.loads((ROOT/'agents/templates/handoff-claude.example.json').read_text())
        self.codex=json.loads((ROOT/'agents/templates/handoff-codex.example.json').read_text())

    def write(self,role='claude',number=1,cycle=1,data=None,explicit=False):
        data=deepcopy(data or getattr(self,role))
        data['rodada']=number
        if cycle>1 or explicit: data['ciclo']=cycle
        name=h.filename(122,number,role,cycle)
        if explicit and cycle==1: name=f'122-c1-r{number}-{role}.json'
        path=self.directory/name
        path.write_text(json.dumps(data))
        return path

    def valid(self,number=1,cycle=1,role=None):
        return h.validate_round(self.project,122,number,cycle,role)

    def approval(self):
        self.claude['veredito']='pode_mergear'
        self.claude['criterios'][0]['status']='atendido'
        self.claude['ajustes']=[]

    def decide(self,value='iterar',cycle=1):
        data={'schema_version':1,'issue':122,'pr':130,'apos_rodada':2,'decisao':value,'autorizado_ate':4,
              'ator':'fixture humana, não real','fonte':'fixture://decisao','registrado_em':'2026-11-13T20:00:00-03:00','motivo':'Fixture'}
        if cycle>1: data['ciclo']=cycle
        path=self.directory/(f'122-c{cycle}-decisao.json' if cycle>1 else '122-decisao.json')
        path.write_text(json.dumps(data))
        return data

    def test_official_pair(self):
        self.write(); self.write('codex')
        result=h.summary(*self.valid())
        self.assertEqual(result['bloqueantes_abertos'],0)
        self.assertFalse(result['pronto_para_humano'])

    def test_approval_allows_suggestions_without_merge_authority(self):
        self.approval()
        self.claude['ajustes']=[{**json.loads((ROOT/'agents/templates/handoff-claude.example.json').read_text())['ajustes'][0],'gravidade':'sugestao'}]
        self.write()
        self.assertTrue(h.summary(*self.valid())['pronto_para_humano'])

    def test_invalid_verdict_ci_unknown_fields_and_empty_criteria(self):
        changes=[lambda d:d.update(veredito='pode_mergear'),lambda d:d['ci'].update(status='pending'),
                 lambda d:d.update(unknown=True),lambda d:d.update(criterios=[]),
                 lambda d:d.update(issue=True),lambda d:d['ci'].update(url='https://user:pass@example.invalid/checks'),
                 lambda d:d.update(gerado_em='2026-11-13T20:00:00'),lambda d:d.update(skills_usadas=['pr-audit'])]
        original=deepcopy(self.claude)
        for change in changes:
            with self.subTest(change=change):
                self.claude=deepcopy(original); change(self.claude); self.write()
                with self.assertRaises(ContractError): self.valid()

    def test_unmet_criterion_and_approval_is_invalid(self):
        self.approval(); self.claude['criterios'][0]['status']='nao_atendido'; self.write()
        with self.assertRaises(ContractError): self.valid()

    def test_adjustments_without_pending_or_blocker_is_invalid(self):
        self.approval(); self.claude['veredito']='ajustes'; self.write()
        with self.assertRaises(ContractError): self.valid()

    def test_response_requires_all_blockers_and_no_new_id(self):
        self.write()
        for changes in [[],[{**self.codex['ajustes'][0],'id':'new'}],[self.codex['ajustes'][0]]*2]:
            self.codex['ajustes']=changes; self.write('codex')
            with self.assertRaises(ContractError): self.valid(role='par')

    def test_response_sha_required_and_candidate_identity_matches(self):
        self.write()
        for key,value in [('pr',99),('candidato',{'base':'main','head':'other','sha':'def456abc'}),
                          ('ajustes',[{**self.codex['ajustes'][0],'commit':None}])]:
            bad={**self.codex,key:value}; self.write('codex',data=bad)
            with self.assertRaises(ContractError): self.valid(role='par')

    def test_explicit_cycle_one_and_collision(self):
        self.write(explicit=True); self.valid()
        self.write()
        with self.assertRaises(ContractError): self.valid()

    def test_new_cycle_does_not_overwrite_first(self):
        first=self.write(); second=self.write(cycle=2)
        self.valid(cycle=2)
        self.assertNotEqual(first,second); self.assertTrue(first.exists())

    def test_filename_must_match_fields(self):
        self.write(data={**self.claude,'issue':123})
        with self.assertRaises(ContractError): self.valid()

    def test_previous_response_and_human_extension_required(self):
        self.write(); self.write('codex'); self.write(number=2)
        self.valid(2)
        self.write(number=3)
        with self.assertRaises(ContractError): self.valid(3)
        self.decide()
        with self.assertRaises((ContractError,OSError)): self.valid(3)
        self.write('codex',number=2)
        self.valid(3)
        self.write('codex',number=3); self.write(number=4)
        self.valid(4)
        self.write('codex',number=4); self.write(number=5)
        with self.assertRaises(ContractError): self.valid(5)

    def test_finalize_never_authorizes_third_round(self):
        for n in (1,2): self.write(number=n); self.write('codex',number=n)
        self.write(number=3); self.decide('finalizar')
        with self.assertRaises(ContractError): self.valid(3)

    def test_symlink_handoff_rejected(self):
        path=self.write(); target=self.project/'other.json'; path.rename(target); path.symlink_to(target)
        with self.assertRaises(ContractError): self.valid()
