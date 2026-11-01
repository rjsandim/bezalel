"""Cenários sintéticos do fluxo; decisões fictícias nunca autorizam trabalho real."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import dream_team
import check_delivery as delivery
import check_repository as repository
import plugin

class DeliveryContractTests(unittest.TestCase):

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.project = Path(temporary.name).resolve()
        self.config = delivery.read_json(ROOT / '.bezalel/project.example.json')
        self.config['production_branches'] = {'principal': 'production'}
        for path in self.config['context'].values():
            self.write(path, 'Contexto sintético; sem serviços conectados.')
        self.write('.bezalel/project.json', json.dumps(self.config))
        self.record = delivery.read_json(ROOT / 'agents/templates/delivery.example.json')
        self.record['issue'] = {'url': 'https://github.com/example/fixture/issues/1', 'scope_ref': 'fixture://scope-v1', 'dependencies': 'Sem dependências nesta fixture.', 'criteria': [{'id': 'AC-01', 'text': 'Resultado observável A'}, {'id': 'AC-02', 'text': 'Resultado observável B'}], 'stories': []}

    def write(self, name, content):
        path = self.project / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path

    def decision(self, subject):
        return {'decision': 'approved', 'subject': subject, 'actor_type': 'human', 'actor': 'fixture-human-not-real', 'source': 'fixture://not-a-real-approval', 'recorded_at': '2026-01-01T12:00:00+00:00'}

    def feature(self):
        self.record['scenario'] = 'feature'
        self.record['issue']['stories'] = [{'url': 'https://github.com/example/fixture/issues/2', 'scope_ref': 'fixture://story-v1', 'criteria': [{'id': 'US-1:AC-01', 'text': 'Critério da história'}]}]
        self.record['issue']['approval'] = self.decision(delivery.scope_subject(self.record['issue']))

    def ready_to_investigate(self):
        self.record.pop('blocker', None)
        self.record['owner'] = 'fixture-developer'
        self.record['implementers'] = ['fixture-developer']
        self.record['isolation'] = {name: {'status': 'not_applicable', 'reason': 'Fixture sem recurso externo.'} for name in delivery.DIMENSIONS}
        self.record['isolation']['files'] = {'status': 'verified', 'evidence': 'fixture://temporary-directory'}

    def ready_to_implement(self):
        self.ready_to_investigate()
        self.record['investigation'] = {'status': 'passed', 'evidence': 'fixture://diagnosis', 'scope': delivery.scope_subject(self.record['issue'])}
        self.record['ui'] = {'status': 'not_applicable', 'reason': 'Fixture sem interface.'}
        self.record['database'] = {'schema_change': False, 'migration': False, 'complex_relations': False, 'reason': 'Sem mudança de banco nesta fixture.'}

    def result(self, **fields):
        return {'status': 'passed', 'evidence': 'fixture://result', 'candidate': self.candidate, **fields}

    def ready_to_accept(self):
        self.ready_to_implement()
        self.record['candidate'] = {'id': 'fixture-candidate-1', 'repositories': [{'name': 'principal', 'base': 'production', 'head': 'fixture-head-1'}], 'context_ref': 'fixture://components-builds-schema-data-config'}
        self.candidate = delivery.candidate_subject(self.record['candidate'], self.config)
        self.record['integration'] = self.result(owner=self.record['owner'])
        self.record['review'] = self.result(reviewer='fixture-tl')
        self.record['checks'] = [self.result(name='test', required=True)]
        self.record['security'] = self.result(reviewer='fixture-appsec', coverage='Fronteiras da fixture', material_gap=False, findings=[])
        criteria = delivery.issue_criteria(self.record['issue'], self.record['scenario'])
        scenario = self.result(name='Dependência indisponível', basis='Risco de integração', expected='Erro explícito sem vazamento')
        self.record['qa'] = self.result(reviewer='fixture-qa', criteria=[self.result(id=c) for c in sorted(criteria)], additional_scenarios=[scenario], journeys=[deepcopy(scenario)])
        self.record['manual_test'] = {'path': 'outputs/roteiro.xlsx', 'candidate': self.candidate}
        path = self.project / 'outputs/roteiro.xlsx'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((ROOT / 'skills/development-test-workbook/assets/test-plan-template.xlsx').read_bytes())

    def ready_to_deliver(self):
        self.ready_to_accept()
        _, subject = delivery.verify_accept_package(self.record, self.project, self.config, delivery.issue_criteria(self.record['issue'], self.record['scenario']))
        self.record['acceptance'] = self.decision(subject)
        self.record['acceptance']['execution_evidence'] = 'fixture://human-cases-not-real'
        self.record['pr_draft'] = 'draft.md'
        self.write('draft.md', 'Rascunho fictício da PR.')

    def ready_to_handoff(self):
        self.ready_to_deliver()
        self.record['pull_requests'] = [{'repository': 'principal', 'url': 'https://github.com/example/fixture/pull/1', 'base': 'production', 'head': 'fixture-head-1', 'state': 'open', 'draft': False, 'verified_at': '2026-01-01T12:00:00+00:00', 'ci': {'status': 'pending', 'evidence': 'fixture://ci-after-open'}}]
        self.record['handoff'] = self.result(next_steps='Humano acompanha CI e decide merge/deploy.')

    def validate(self, stage='deliver'):
        delivery.validate_delivery(self.record, self.project, stage, self.config)

    def test_draft_allows_minimal_intent_but_not_implementation(self):
        self.record['issue'] = {'url': 'https://github.com/example/fixture/issues/1'}
        self.validate('plan')
        with self.assertRaises(delivery.ContractError):
            self.validate('implement')

    def test_investigation_must_precede_implementation(self):
        self.ready_to_investigate()
        self.validate('investigate')
        with self.assertRaises(delivery.ContractError):
            self.validate('implement')
        self.ready_to_implement()
        self.validate('implement')

    def test_all_isolation_dimensions_are_required(self):
        self.ready_to_investigate()
        baseline = deepcopy(self.record)
        for dimension in delivery.DIMENSIONS:
            with self.subTest(dimension=dimension):
                self.record = deepcopy(baseline)
                del self.record['isolation'][dimension]
                with self.assertRaises(delivery.ContractError):
                    self.validate('investigate')

    def test_files_require_evidence(self):
        self.ready_to_investigate()
        for result in [{'status': 'not_applicable', 'reason': 'none'}, {'status': 'verified', 'evidence': ''}, {'status': 'pending'}]:
            self.record['isolation']['files'] = result
            with self.assertRaises(delivery.ContractError):
                self.validate('investigate')

    def test_integrator_is_a_developer(self):
        self.ready_to_implement()
        self.record['owner'] = 'fixture-tl'
        with self.assertRaises(delivery.ContractError):
            self.validate('implement')

    def test_feature_scope_changes_invalidate_decision(self):
        self.feature()
        self.ready_to_investigate()
        self.validate('investigate')
        self.record['issue']['stories'][0]['criteria'][0]['text'] = 'Escopo alterado'
        with self.assertRaises(delivery.ContractError):
            self.validate('investigate')

    def test_feature_requires_stories_and_unique_criteria(self):
        self.feature()
        baseline = deepcopy(self.record['issue'])
        for stories in [[], [baseline['stories'][0], baseline['stories'][0]]]:
            self.record['issue']['stories'] = stories
            with self.assertRaises(delivery.ContractError):
                delivery.issue_criteria(self.record['issue'], 'feature')
        self.record['issue'] = baseline
        self.record['issue']['stories'][0]['criteria'][0]['id'] = 'AC-01'
        with self.assertRaises(delivery.ContractError):
            delivery.issue_criteria(self.record['issue'], 'feature')

    def test_ui_requires_independent_current_mock_review(self):
        self.ready_to_implement()
        self.record['ui'] = {'status': 'passed', 'reviewer': 'fixture-qa', 'scope': delivery.scope_subject(self.record['issue']), 'mock_ref': 'fixture://mock', 'evidence': 'fixture://ui'}
        self.validate('implement')
        baseline = deepcopy(self.record['ui'])
        for key, value in [('reviewer', 'fixture-developer'), ('scope', 'old'), ('mock_ref', ''), ('status', 'failed')]:
            self.record['ui'] = {**baseline, key: value}
            with self.assertRaises(delivery.ContractError):
                self.validate('implement')

    def database_decision(self, impact):
        self.ready_to_implement()
        proposal = self.write('.bezalel/reviews/proposal.html', '<!doctype html><html lang="pt-BR"><body>Estrutura sintética antes/depois.</body></html>')
        database = self.record['database']
        database.update({impact: True, 'proposal': '.bezalel/reviews/proposal.html',
                         'proposal_sha256': delivery.file_digest(proposal), 'base_ref': 'fixture-base-1',
                         'scope': delivery.scope_subject(self.record['issue']),
                         'summary': 'Fixture: coluna proposta; não representa banco real.',
                         'proposal_ref': 'fixture://task-proposal'})
        subject = delivery.proposal_subject(database)
        database['review'] = {'status': 'passed', 'reviewer': 'fixture-tl', 'subject': subject, 'evidence': 'fixture://technical-review'}
        self.validate('database')
        database['approval'] = self.decision(subject)
        proposal.unlink()
        database['cleanup'] = {'status': 'deleted', 'deleted_at': '2026-01-01T12:01:00+00:00', 'evidence': 'fixture://deleted-after-decision'}
        return proposal

    def test_each_database_trigger_requires_human_approval(self):
        for impact in ['schema_change', 'migration', 'complex_relations']:
            with self.subTest(impact=impact):
                self.database_decision(impact)
                self.validate('implement')
                del self.record['database']['approval']
                with self.assertRaises(delivery.ContractError):
                    self.validate('implement')

    def test_complex_relations_require_identified_technical_review(self):
        self.database_decision('complex_relations')
        del self.record['database']['review']
        with self.assertRaises(delivery.ContractError):
            self.validate('implement')

    def test_database_change_invalidates_approval(self):
        self.database_decision('schema_change')
        self.record['database']['base_ref'] = 'fixture-base-changed'
        with self.assertRaisesRegex(delivery.ContractError, 'versão aprovada'):
            self.validate('implement')

    def test_human_decision_fields_are_required(self):
        self.database_decision('migration')
        baseline = deepcopy(self.record['database']['approval'])
        for key, value in [('actor_type', 'agent'), ('actor', ''), ('source', ''), ('recorded_at', None), ('recorded_at', '2026-01-01T12:00:00'), ('decision', 'pending')]:
            self.record['database']['approval'] = {**baseline, key: value}
            with self.assertRaises(delivery.ContractError):
                self.validate('implement')

    def test_no_database_change_rejects_fake_approval(self):
        self.ready_to_implement()
        self.record['database']['approval'] = {'decision': 'approved'}
        with self.assertRaises(delivery.ContractError):
            self.validate('implement')

    def test_html_review_adjustment_and_deletion_have_distinct_gates(self):
        path = self.database_decision('schema_change')
        self.validate('implement')
        path.write_text('<!doctype html><html><body>Proposta ajustada.</body></html>')
        with self.assertRaises(delivery.ContractError):
            self.validate('database')
        self.record['database']['proposal_sha256'] = delivery.file_digest(path)
        self.validate('database')
        with self.assertRaises(delivery.ContractError):
            self.validate('implement')
        self.record['database']['approval'] = self.decision(delivery.proposal_subject(self.record['database']))
        with self.assertRaises(delivery.ContractError):
            self.validate('implement')  # HTML ainda não foi excluído.
        path.unlink()
        self.validate('implement')

    def test_html_cleanup_requires_evidence_after_real_decision(self):
        self.database_decision('migration')
        original = deepcopy(self.record['database']['cleanup'])
        for change in [{'status': 'pending'}, {'evidence': ''}, {'deleted_at': '2026-01-01T11:59:00+00:00'}]:
            self.record['database']['cleanup'] = {**original, **change}
            with self.assertRaises(delivery.ContractError):
                self.validate('implement')
        self.record['database']['cleanup'] = original
        self.record['database']['approval']['decision'] = 'rejected'
        with self.assertRaises(delivery.ContractError):
            self.validate('implement')

    def test_html_path_cannot_escape_or_follow_a_link_even_after_deletion(self):
        self.database_decision('schema_change')
        original = self.record['database']['proposal']
        for path in ['proposal.md', '../proposal.html', '.bezalel/reviews/../outside.html']:
            self.record['database']['proposal'] = path
            with self.assertRaises(delivery.ContractError):
                self.validate('implement')
        self.record['database']['proposal'] = original
        (self.project / original).symlink_to(self.project / 'absent.html')
        with self.assertRaises(delivery.ContractError):
            self.validate('implement')

    def ready_to_finish(self):
        self.ready_to_handoff()
        self.record['pull_requests'][0].update(state='merged', merged_at='2026-01-01T12:02:00+00:00',
            verified_at='2026-01-01T12:03:00+00:00', merge_commit='fixture-squash-commit', evidence='fixture://github-query')
        environment = {'project': 'fixture', 'repository': 'principal', 'branch': 'feat/example',
                       'worktree': str(self.project / 'worktree'), 'name': 'feature-example',
                       'docker_context': 'fixture-context', 'ownership_evidence': 'fixture://saved-env-identity'}
        self.record['environment'] = environment
        self.record['completion'] = {
            'trigger': {'kind': 'merge_reported', 'actor_type': 'human', 'actor': 'fixture-human',
                        'source': 'fixture://message', 'recorded_at': '2026-01-01T12:01:00+00:00', 'candidate': self.candidate},
            'scope_complete': True, 'scope_evidence': 'fixture://all-scope-resolved',
            'issues': [{'url': self.record['issue']['url'], 'state': 'closed',
                        'verified_at': '2026-01-01T12:04:00+00:00', 'evidence': 'fixture://issue-query'}],
            'environment': {'target': delivery.environment_subject(environment), 'status': 'destroyed',
                            'worktree_removed': True, 'preservation_evidence': 'fixture://verified-backup',
                            'command_evidence': 'fixture://destroy-result', 'evidence': 'fixture://removed-targets',
                            'verified_at': '2026-01-01T12:05:00+00:00'}}

    def test_approval_or_merge_report_never_substitutes_verified_merge(self):
        self.ready_to_finish()
        for kind in ['approved', 'merge_reported']:
            self.record['completion']['trigger']['kind'] = kind
            for state in ['open', 'closed', 'unknown']:
                self.record['pull_requests'][0]['state'] = state
                with self.assertRaises(delivery.ContractError):
                    self.validate('merged')
        self.record['pull_requests'][0]['state'] = 'merged'
        self.validate('merged')
        self.validate('finish')

    def test_post_merge_query_must_cover_current_version_and_follow_message(self):
        self.ready_to_finish()
        original = deepcopy(self.record['pull_requests'][0])
        for change in [{'head': 'other-head'}, {'base': 'other-base'}, {'merge_commit': ''},
                       {'evidence': ''}, {'verified_at': '2026-01-01T12:00:00+00:00'}]:
            self.record['pull_requests'][0] = {**original, **change}
            with self.assertRaises(delivery.ContractError):
                self.validate('merged')

    def test_all_repository_merges_are_required_before_cleanup(self):
        self.ready_to_finish()
        self.config['production_branches']['web'] = 'production'
        self.record['candidate']['repositories'].append({'name': 'web', 'base': 'production', 'head': 'web-head'})
        self.record['completion']['trigger']['candidate'] = delivery.candidate_subject(self.record['candidate'], self.config)
        with self.assertRaises(delivery.ContractError):
            self.validate('merged')
        self.record['pull_requests'].append({**self.record['pull_requests'][0], 'repository': 'web',
                                           'url': 'https://github.com/example/web/pull/2', 'head': 'web-head', 'state': 'open'})
        with self.assertRaises(delivery.ContractError):
            self.validate('merged')
        self.record['pull_requests'][1]['state'] = 'merged'
        self.validate('finish')

    def test_closure_failure_or_remaining_scope_blocks_complete_cleanup(self):
        self.ready_to_finish()
        self.record['completion']['issues'][0]['state'] = 'open'
        self.validate('merged')
        with self.assertRaises(delivery.ContractError):
            self.validate('finish')
        self.record['completion']['issues'][0]['state'] = 'closed'
        self.record['completion']['scope_complete'] = False
        with self.assertRaises(delivery.ContractError):
            self.validate('finish')

    def test_missing_issue_and_unmanaged_environment_are_explicitly_not_applicable(self):
        self.record['issue']['url'] = None
        self.ready_to_handoff()
        self.validate('handoff')
        self.record['issue']['url'] = 'https://github.com/example/fixture/issues/1'
        self.ready_to_finish()
        self.record['issue']['url'] = None
        self.record['completion']['issues'] = []
        self.record['environment'] = {'status': 'not_applicable', 'reason': 'Fixture sem ENV', 'evidence': 'fixture://no-env'}
        self.record['completion']['environment'] = {'status': 'not_applicable', 'evidence': 'fixture://confirmed-no-env'}
        self.validate('finish')

    def test_destroy_result_must_match_saved_target_and_preservation(self):
        self.ready_to_finish()
        original = deepcopy(self.record['completion']['environment'])
        for change in [{'target': 'other'}, {'preservation_evidence': ''}, {'status': 'partial'},
                       {'worktree_removed': False}, {'verified_at': '2026-01-01T12:00:00+00:00'}]:
            self.record['completion']['environment'] = {**original, **change}
            with self.assertRaises(delivery.ContractError):
                self.validate('finish')
        self.record['completion']['environment'] = original
        self.record['environment']['branch'] = 'production'
        self.record['completion']['environment']['target'] = delivery.environment_subject(self.record['environment'])
        with self.assertRaises(delivery.ContractError):
            self.validate('finish')

    def test_finish_does_not_require_deleted_worktree_artifacts(self):
        self.ready_to_finish()
        (self.project / self.record['manual_test']['path']).unlink()
        (self.project / self.record['pr_draft']).unlink()
        self.validate('finish')

    def test_feature_without_github_issues_preserves_stories_and_human_scope(self):
        self.feature()
        self.record['issue']['url'] = None
        self.record['issue']['stories'][0]['url'] = None
        self.record['issue']['approval'] = self.decision(delivery.scope_subject(self.record['issue']))
        self.ready_to_handoff()
        self.validate('handoff')
        del self.record['issue']['approval']
        with self.assertRaises(delivery.ContractError):
            self.validate('handoff')

    def test_disposition_without_issue_cannot_fabricate_remote_closure(self):
        self.record['issue']['url'] = None
        self.record.pop('blocker', None)
        self.record['disposition'] = {'kind': 'discarded', 'reason': 'Fixture encerrada',
                                      'evidence': 'fixture://message', 'issue_state': 'not_applicable'}
        self.record['disposition']['approval'] = self.decision(delivery.disposition_subject(self.record))
        self.validate('close')
        self.record['disposition']['issue_state'] = 'closed'
        with self.assertRaises(delivery.ContractError):
            self.validate('close')

    def test_finish_cli_uses_saved_record_without_running_commands_or_requiring_old_files(self):
        self.ready_to_finish()
        for path in [self.record['manual_test']['path'], self.record['pr_draft'], *self.config['context'].values()]:
            (self.project / path).unlink()
        marker = self.project / 'must-not-run'
        self.config['checks']['test'] = [sys.executable, '-c', 'from pathlib import Path; Path(' + repr(str(marker)) + ').touch()']
        self.write('.bezalel/project.json', json.dumps(self.config))
        self.write('.bezalel/deliveries/fixture.local.json', json.dumps(self.record))
        result = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/check_delivery.py'), '--project', str(self.project),
                                 '--record', '.bezalel/deliveries/fixture.local.json', '--stage', 'finish'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(marker.exists())

    def test_native_package_delivery_checker_reads_packaged_contracts(self):
        self.ready_to_handoff()
        self.record.pop('acceptance', None)
        self.write('.bezalel/deliveries/fixture.local.json', json.dumps(self.record))
        package = self.project / 'native-package'
        plugin.build(ROOT, package)
        result = subprocess.run([sys.executable, '-B', str(package / 'scripts/check_delivery.py'),
                                 '--project', str(self.project), '--record', '.bezalel/deliveries/fixture.local.json',
                                 '--stage', 'handoff'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_all_three_scenarios_complete_synthetic_handoff(self):
        for scenario in ['bug', 'improvement', 'feature']:
            with self.subTest(scenario=scenario):
                self.setUp()
                self.record['scenario'] = scenario
                if scenario == 'feature':
                    self.feature()
                self.ready_to_handoff()
                self.validate('handoff')

    def test_each_review_must_be_independent_of_implementers(self):
        self.ready_to_accept()
        for key in ['review', 'security', 'qa']:
            old = self.record[key]['reviewer']
            self.record[key]['reviewer'] = ' fixture-developer '
            with self.assertRaises(delivery.ContractError):
                self.validate('accept')
            self.record[key]['reviewer'] = old

    def test_failed_or_missing_mandatory_check_blocks_acceptance(self):
        self.ready_to_accept()
        original = deepcopy(self.record['checks'])
        for checks in [[], [{**original[0], 'status': 'failed'}], [{**original[0], 'status': 'not_applicable', 'reason': 'fixture'}]]:
            self.record['checks'] = checks
            with self.assertRaises(delivery.ContractError):
                self.validate('accept')

    def test_candidate_change_invalidates_evidence(self):
        self.ready_to_deliver()
        self.record['candidate']['repositories'][0]['head'] = 'changed'
        with self.assertRaises(delivery.ContractError):
            self.validate()

    def test_review_evidence_cannot_be_reused_for_wrong_candidate(self):
        self.ready_to_accept()
        for key in ['review', 'security', 'qa', 'integration']:
            self.record[key]['candidate'] = 'old'
            with self.assertRaises(delivery.ContractError):
                self.validate('accept')
            self.record[key]['candidate'] = self.candidate

    def test_security_material_gap_blocks(self):
        self.ready_to_accept()
        self.record['security']['material_gap'] = True
        with self.assertRaises(delivery.ContractError):
            self.validate('accept')

    def risk(self, severity='medium'):
        finding = {'id': 'F1', 'summary': 'Achado sintético', 'classification': 'confirmed', 'confidence': 'high', 'severity': severity, 'evidence': 'fixture://finding', 'disposition': 'deferred', 'reason': 'Decisão sintética', 'owner': 'fixture-owner', 'deadline_or_condition': '2026-12-01'}
        subject = 'risk:' + delivery.digest({'candidate': self.candidate, 'finding': finding})
        finding['approval'] = self.decision(subject)
        self.record['security']['findings'] = [finding]
        return finding

    def test_medium_risk_needs_exact_human_deferral(self):
        self.ready_to_accept()
        finding = self.risk()
        self.validate('accept')
        finding['deadline_or_condition'] = 'alterado'
        with self.assertRaises(delivery.ContractError):
            self.validate('accept')

    def test_high_and_critical_risks_cannot_be_deferred(self):
        self.ready_to_accept()
        for severity in ['high', 'critical']:
            self.risk(severity)
            with self.assertRaises(delivery.ContractError):
                self.validate('accept')

    def test_unresolved_security_hypothesis_blocks(self):
        self.ready_to_accept()
        finding = self.risk()
        finding['disposition'] = 'investigating'
        with self.assertRaises(delivery.ContractError):
            self.validate('accept')

    def test_qa_requires_each_criterion_once_and_passing(self):
        self.ready_to_accept()
        criteria = deepcopy(self.record['qa']['criteria'])
        for results in [criteria[:1], [criteria[0], criteria[0]], [*criteria, criteria[0]], [criteria[0], {**criteria[1], 'status': 'failed'}]]:
            self.record['qa']['criteria'] = results
            with self.assertRaises(delivery.ContractError):
                self.validate('accept')

    def test_qa_additional_scenario_requires_basis_and_expected_result(self):
        self.ready_to_accept()
        item = deepcopy(self.record['qa']['additional_scenarios'][0])
        for results in [[], [{**item, 'basis': ''}], [{**item, 'expected': ''}], [{**item, 'status': 'failed'}]]:
            self.record['qa']['additional_scenarios'] = results
            with self.assertRaises(delivery.ContractError):
                self.validate('accept')

    def test_feature_global_journey_failure_and_resumption(self):
        self.feature()
        self.ready_to_accept()
        self.record['qa']['journeys'][0]['status'] = 'failed'
        with self.assertRaises(delivery.ContractError):
            self.validate('accept')
        self.record['qa']['journeys'][0]['status'] = 'passed'
        self.validate('accept')

    def test_excel_required_for_improvement_and_feature(self):
        self.record['scenario'] = 'improvement'
        self.ready_to_accept()
        self.record['manual_test']['path'] = 'guide.md'
        self.write('guide.md', 'Guia sintético')
        with self.assertRaises(delivery.ContractError):
            self.validate('accept')
        self.record['manual_test']['path'] = 'fake.xlsx'
        self.write('fake.xlsx', 'Não é Excel')
        with self.assertRaises(delivery.ContractError):
            self.validate('accept')

    def test_package_is_not_human_acceptance(self):
        self.ready_to_handoff()
        self.record.pop('acceptance', None)
        self.validate('deliver')
        self.validate('handoff')
        with self.assertRaises(delivery.ContractError):
            self.validate('accepted')

    def test_human_acceptance_requires_execution_and_current_workbook(self):
        self.ready_to_handoff()
        self.record['acceptance']['execution_evidence'] = ''
        with self.assertRaises(delivery.ContractError):
            self.validate('accepted')
        self.record['acceptance']['execution_evidence'] = 'fixture://not-real'
        path = self.project / self.record['manual_test']['path']
        path.write_bytes(path.read_bytes() + b'changed')
        with self.assertRaises(delivery.ContractError):
            self.validate('accepted')

    def test_missing_pr_or_wrong_base_blocks_handoff(self):
        self.ready_to_handoff()
        pr = deepcopy(self.record['pull_requests'][0])
        for prs in [[], [{**pr, 'base': 'wrong'}], [{**pr, 'head': 'old'}], [{**pr, 'state': 'closed'}]]:
            self.record['pull_requests'] = prs
            with self.assertRaises(delivery.ContractError):
                self.validate('handoff')

    def test_open_draft_or_unverified_readiness_blocks_handoff_and_acceptance(self):
        self.ready_to_handoff()
        pr = self.record['pull_requests'][0]
        for value in [True, None, 'false', 0]:
            with self.subTest(draft=value):
                pr['draft'] = value
                for stage in ['handoff', 'accepted']:
                    with self.assertRaisesRegex(delivery.ContractError, 'draft false'):
                        self.validate(stage)
        pr.pop('draft')
        with self.assertRaises(delivery.ContractError):
            self.validate('handoff')
        pr['draft'] = False
        self.validate('handoff')
        self.validate('accepted')

    def test_post_open_ci_may_be_pending_or_failed_when_reported(self):
        self.ready_to_handoff()
        for status in ['pending', 'failed', 'passed', 'not_applicable']:
            self.record['pull_requests'][0]['ci']['status'] = status
            self.validate('handoff')
        self.record['handoff']['next_steps'] = ''
        with self.assertRaises(delivery.ContractError):
            self.validate('handoff')

    def test_multiple_repositories_require_distinct_complete_prs(self):
        self.ready_to_handoff()
        self.config['production_branches']['web'] = 'live'
        self.record['candidate']['repositories'].append({'name': 'web', 'base': 'live', 'head': 'fixture-web-1'})
        new_candidate = delivery.candidate_subject(self.record['candidate'], self.config)

        def rebind(value):
            if isinstance(value, dict):
                return {k: rebind(v) for k, v in value.items()}
            if isinstance(value, list):
                return [rebind(v) for v in value]
            return new_candidate if value == self.candidate else value
        self.record = rebind(self.record)
        _, subject = delivery.verify_accept_package(self.record, self.project, self.config, delivery.issue_criteria(self.record['issue'], 'bug'))
        self.record['acceptance'] = {**self.decision(subject), 'execution_evidence': 'fixture://human-not-real'}
        with self.assertRaises(delivery.ContractError):
            self.validate('handoff')
        second = {**self.record['pull_requests'][0], 'repository': 'web', 'base': 'live', 'head': 'fixture-web-1'}
        self.record['pull_requests'].append(second)
        with self.assertRaises(delivery.ContractError):
            self.validate('handoff')
        second['url'] = 'https://github.com/example/web/pull/2'
        self.validate('handoff')

    def test_configured_production_branch_is_enforced(self):
        self.ready_to_accept()
        self.config['production_branches']['principal'] = 'other'
        with self.assertRaises(delivery.ContractError):
            self.validate('accept')

    def test_bug_missing_tool_blocks_then_resumes(self):
        self.ready_to_implement()
        self.record['blocker'] = {'reason': 'Ferramenta/prova ausente', 'owner': 'fixture-developer', 'resume_condition': 'Obter prova autorizada'}
        with self.assertRaises(delivery.ContractError):
            self.validate('implement')
        del self.record['blocker']
        self.validate('implement')

    def test_improvement_bank_pending_then_resumes(self):
        self.record['scenario'] = 'improvement'
        self.database_decision('complex_relations')
        decision = self.record['database'].pop('approval')
        with self.assertRaises(delivery.ContractError):
            self.validate('implement')
        self.record['database']['approval'] = decision
        self.validate('implement')

    def test_nonimplementation_destinations_do_not_require_fake_tests(self):
        self.record.pop('blocker')
        self.record['issue'] = {'url': 'https://github.com/example/fixture/issues/1'}
        for kind, state in [('deferred', 'open'), ('discarded', 'closed'), ('expected_behavior', 'closed'), ('transferred', 'open')]:
            disposition = {'kind': kind, 'reason': 'Decisão sintética', 'issue_state': state, 'evidence': 'fixture://state', 'owner': 'fixture-pm', 'resume_condition': 'Orientação humana', 'target': 'feature', 'target_started_evidence': 'fixture://same-issue-target'}
            self.record['disposition'] = disposition
            disposition['approval'] = self.decision(delivery.disposition_subject(self.record))
            self.validate('close')
            disposition['issue_state'] = 'unknown'
            with self.assertRaises(delivery.ContractError):
                self.validate('close')

    def test_deferred_intent_cannot_advance_as_implementation(self):
        self.ready_to_implement()
        self.record['disposition'] = {'kind': 'deferred'}
        with self.assertRaises(delivery.ContractError):
            self.validate('implement')

    def test_paths_cannot_escape_project_or_follow_external_symlink(self):
        with tempfile.TemporaryDirectory() as outside:
            secret = Path(outside) / 'private.md'
            secret.write_text('PRIVATE_FIXTURE_VALUE')
            (self.project / 'linked.md').symlink_to(secret)
            for value in [str(secret), 'linked.md', '../missing.md']:
                with self.assertRaises(delivery.ContractError):
                    delivery.local_file(self.project, value, 'Fixture')

    def test_invalid_json_diagnostic_omits_content(self):
        path = self.write('invalid.json', 'PRIVATE_FIXTURE_VALUE')
        with self.assertRaises(delivery.ContractError) as caught:
            delivery.read_json(path)
        self.assertNotIn('PRIVATE_FIXTURE_VALUE', str(caught.exception))

    def test_v1_and_permission_grants_are_rejected(self):
        for field, value in [('permissions', {'push': True}), ('observers', {}), ('schema_version', 1)]:
            config = {**self.config, field: value}
            with self.assertRaises(delivery.ContractError):
                delivery.validate_config(config, self.project)
        self.record['schema_version'] = 1
        with self.assertRaises(delivery.ContractError):
            self.validate('plan')

    def test_cli_is_read_only_and_does_not_execute_configured_commands(self):
        self.ready_to_deliver()
        self.config['checks']['test'] = [sys.executable, '-c', "from pathlib import Path; Path('SHOULD_NOT_EXIST').touch()"]
        self.write('.bezalel/project.json', json.dumps(self.config))
        self.write('.bezalel/deliveries/fixture.local.json', json.dumps(self.record))
        before = {str(p): p.read_bytes() for p in self.project.rglob('*') if p.is_file()}
        result = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/check_delivery.py'), '--project', str(self.project), '--record', '.bezalel/deliveries/fixture.local.json', '--stage', 'deliver'], cwd=self.project, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Não comprova', result.stdout)
        self.assertEqual(before, {str(p): p.read_bytes() for p in self.project.rglob('*') if p.is_file()})

    def test_catalog_roles_and_human_boundary(self):
        catalog = delivery.read_json(ROOT / 'agents/catalog.json')
        self.assertEqual(set(catalog['roles']), {'produto', 'coordenador', 'infraestrutura', 'dev-fullstack', 'backend', 'frontend-web', 'mobile', 'qa', 'appsec'})
        self.assertEqual(sum((len(r['processes']) for r in catalog['roles'].values())), 17)
        self.assertEqual(len(catalog['external_actors']['aprovador-humano']['processes']), 4)
        for role in ['aprovador-humano', 'observador-negocio']:
            self.record['roles'] = [role]
            with self.assertRaises(delivery.ContractError):
                self.validate('plan')

    def test_catalog_drift_and_missing_process_are_rejected(self):
        original_read = repository.read_json
        baseline = original_read(ROOT / 'agents/catalog.json')
        for mutate in [lambda c: c['roles']['qa'].update(display_name='Outro'), lambda c: c['roles']['appsec'].update(processes=[]), lambda c: c['roles']['coordenador']['processes'][0].update(skills=[])]:
            catalog = deepcopy(baseline)
            mutate(catalog)
            with patch.object(repository, 'read_json', side_effect=lambda path: catalog if path.name == 'catalog.json' else original_read(path)):
                self.assertTrue(repository.validate_agents())

    def test_malformed_catalog_has_safe_diagnostic(self):
        self.write('agents/catalog.json', '[]')
        with patch.object(repository, 'ROOT', self.project):
            self.assertTrue(repository.validate_agents())
        with patch.object(delivery, 'ROOT', self.project):
            with self.assertRaises(delivery.ContractError):
                self.validate('plan')

    def test_adapter_cannot_omit_contract_or_change_permissions(self):
        for adapter in [{'name': 'wrong', 'description': 'fixture', 'developer_instructions': 'missing'}, {'name': 'dream-team-produto', 'description': 'fixture', 'developer_instructions': 'agents/roles/produto.md agents/dream-team.md', 'approval_policy': 'never'}]:
            with patch.object(repository.tomllib, 'loads', return_value=adapter):
                self.assertTrue(repository.validate_agents())

    def test_adapters_must_match_catalog_and_template(self):
        expected = dream_team.render(ROOT)
        self.assertEqual(dream_team.divergent(ROOT), [])
        self.assertEqual(len(expected), 18)
        changed = {**expected, 'claude/dream-team-qa.md': expected['claude/dream-team-qa.md'] + 'Linha manual.\n'}
        with patch.object(repository, 'expected_files', return_value={**dream_team.expected_files(ROOT), **changed}):
            self.assertTrue(repository.validate_generated())
            self.assertEqual(repository.validate_agents(), [])
        with self.assertRaises(ValueError):
            dream_team.quoted('Descrição com "aspas"')

    def test_process_files_and_index_must_match_catalog(self):
        expected = dream_team.expected_files(ROOT)
        flow = 'dream-team.md'
        self.assertIn('<a id="process-qa"></a>', expected[flow])
        stale = {**expected, flow: expected[flow].replace('2. **Executar critérios e jornadas.** Skills: agent-browser.', '2. **Executar critérios e jornadas.**')}
        with patch.object(repository, 'expected_files', return_value=stale):
            self.assertTrue(repository.validate_generated())
        original_read = repository.read_json
        baseline = original_read(ROOT / 'agents/catalog.json')
        for mutate in [lambda c: c['roles']['qa']['processes'][0].update(file='processes/qa.md'),
                       lambda c: c['roles']['qa']['processes'][0].update(file='roles/qa.md')]:
            catalog = deepcopy(baseline)
            mutate(catalog)
            with patch.object(repository, 'read_json', side_effect=lambda path: catalog if path.name == 'catalog.json' else original_read(path)):
                self.assertTrue(repository.validate_agents())
        # Cada papel lê somente os próprios processos.
        qa = expected['codex/dream-team-qa.toml']
        self.assertIn('agents/processes/ui.md, agents/processes/qa.md', qa)
        self.assertNotIn('agents/processes/plan.md', qa)
        self.assertNotIn('agents/README.md', qa)

    def test_package_catalog_links_and_adapters_are_consistent(self):
        self.assertEqual(repository.validate_agents(), [])
        self.assertEqual(repository.validate_generated(), [])
        self.assertEqual(repository.validate_structure(repository.package_files()), [])
if __name__ == '__main__':
    unittest.main()
