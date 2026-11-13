"""CI simulada sem rede; nenhum resultado verde por ausência ou erro."""
import json
from pathlib import Path
import sys
import subprocess
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import ci_gate as ci
from check_delivery import ContractError


class CIGateTests(unittest.TestCase):
    def setUp(self):
        self.pr={'number':130,'url':'https://github.com/example/fixture/pull/130','state':'OPEN',
                 'isDraft':False,'headRefOid':'abc123def'}

    def gate(self,checks,required=None,dry=True):
        def read(project,pr,only_required): return checks if required is None or not only_required else required
        with patch.object(ci,'pr_info',return_value=self.pr),patch.object(ci,'read_checks',side_effect=read):
            return ci.gate(Path('.'),130,0,1,dry)

    def test_pass_fail_cancel_pending_mixed_and_empty(self):
        for buckets,code in [(['pass'],0),(['pass','fail'],2),(['cancel'],2),(['pending'],3),(['skip'],3),([],3),(['pass','pending'],3)]:
            with self.subTest(buckets=buckets):
                checks=[{'name':f'check-{i}','bucket':b,'link':'https://github.com/example/fixture/actions/runs/1'} for i,b in enumerate(buckets)]
                result,summary=self.gate(checks)
                self.assertEqual(result,code)
                self.assertEqual(summary['sha'],'abc123def')

    def test_required_checks_are_used_and_all_fallback_is_explicit(self):
        code,result=self.gate([{'name':'optional','bucket':'fail'}],[{'name':'required','bucket':'pass'}])
        self.assertEqual(code,0); self.assertEqual(result['scope'],'required')
        code,result=self.gate([{'name':'all','bucket':'fail'}],[])
        self.assertEqual(code,2); self.assertEqual(result['scope'],'all')

    def test_changed_head_invalidates_green_result(self):
        with patch.object(ci,'pr_info',side_effect=[self.pr,{**self.pr,'headRefOid':'def456abc'}]),patch.object(ci,'read_checks',return_value=[{'name':'tests','bucket':'pass'}]):
            self.assertEqual(ci.observe(Path('.'),130)['status'],'pending')

    def test_poll_and_dry_run(self):
        states=[{'status':'pending'},{'status':'passed'}]
        with patch.object(ci,'observe',side_effect=states),patch.object(ci.time,'sleep') as sleep:
            self.assertEqual(ci.gate(Path('.'),130,10,1)[0],0); sleep.assert_called_once()
        with patch.object(ci,'observe',return_value=states[0]),patch.object(ci.time,'sleep') as sleep:
            self.assertEqual(ci.gate(Path('.'),130,10,1,True)[0],3); sleep.assert_not_called()

    def test_access_failure_is_not_no_required_checks(self):
        result=subprocess.CompletedProcess([],1,'','authentication failed: private fixture')
        with patch.object(ci,'gh',return_value=result):
            with self.assertRaises(ContractError): ci.read_checks(Path('.'),130,True)
        result=subprocess.CompletedProcess([],1,'','no required checks reported on the branch')
        with patch.object(ci,'gh',return_value=result):
            self.assertEqual(ci.read_checks(Path('.'),130,True),[])

    def test_optional_error_with_unknown_bucket_is_not_success(self):
        with patch.object(ci,'gh',return_value=subprocess.CompletedProcess([],1,json.dumps([{'name':'a','bucket':'pass'}]),'')):
            with self.assertRaises(ContractError): ci.read_checks(Path('.'),130,False)

    def test_command_preserves_tool_failure_without_echoing_private_output(self):
        with patch.object(ci.subprocess,'run',return_value=subprocess.CompletedProcess([],9,'private-fixture','private-fixture')):
            with self.assertRaisesRegex(ContractError,'diagnóstico omitido'): ci.gh(Path('.'),'pr','checks')
