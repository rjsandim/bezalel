"""Contract checks using fictional artifacts; no approval here authorizes real work."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import check_delivery as delivery
import check_repository as repository


class DeliveryContractTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.project = Path(temporary.name).resolve()
        self.config = json.loads((ROOT / ".bezalel/project.example.json").read_text())
        self.record = json.loads((ROOT / "agents/templates/delivery.example.json").read_text())
        self.write("stories/US-001.md", (ROOT / "agents/examples/US-001.md").read_text())
        for reference in self.config["context"].values():
            self.write(reference, "Contexto sintético de teste, sem serviços.")

    def write(self, name, content):
        path = self.project / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path

    def ready_to_implement(self):
        self.record["owner"] = "fixture-coordinator"
        self.record["implementers"] = ["fixture-developer"]
        self.record["isolation"] = {
            name: {"status": "not_applicable", "reason": "Fixture sem recurso externo."}
            for name in delivery.DIMENSIONS
        }
        self.record["isolation"]["files"] = {"status": "verified", "evidence": "fixture://temporary-directory"}

    def ready_to_deliver(self):
        self.ready_to_implement()
        self.record["checks"] = [{"name": "fixture-test", "status": "passed", "evidence": "fixture://result"}]
        self.record["qa"] = {
            "reviewer": "fixture-independent-reviewer",
            "criteria": [{"id": criterion, "status": "passed", "evidence": "fixture://observed"} for criterion in ["AC-01", "AC-02"]],
            "additional_scenarios": [{"name": "Dependência indisponível", "basis": "Risco de integração", "expected": "Falha visível sem expor dados", "status": "passed", "evidence": "fixture://negative-result"}],
        }
        self.record["integration"] = {"owner": self.record["owner"], "status": "passed", "evidence": "fixture://integrated-flow"}
        for key in ["manual_test", "pr_draft"]:
            self.record[key] = key + ".md"
            self.write(self.record[key], "Artefato sintético de validação.")

    def synthetic_database_decision(self):
        proposal = self.write("proposal.md", "Proposta fictícia, usada somente em testes.")
        self.record["database"] = {
            "change": "structural", "proposal": "proposal.md",
            "approval": {"decision": "approved", "actor_type": "human", "actor": "fixture-human-not-real", "source": "fixture://not-a-real-approval", "recorded_at": "2026-01-01T12:00:00+00:00", "proposal_sha256": hashlib.sha256(proposal.read_bytes()).hexdigest()},
        }
        return proposal

    def validate(self, stage="deliver"):
        delivery.validate_delivery(self.record, self.project, stage)

    def test_draft_plans_but_does_not_allow_implementation(self):
        self.validate("plan")
        with self.assertRaises(delivery.ContractError):
            self.validate("implement")

    def test_isolated_nonstructural_work_can_implement(self):
        self.ready_to_implement()
        self.validate("implement")
        self.record["database"]["reason"] = ""
        with self.assertRaises(delivery.ContractError):
            self.validate("implement")

    def test_every_isolation_dimension_is_required(self):
        self.ready_to_implement()
        baseline = deepcopy(self.record)
        for dimension in delivery.DIMENSIONS:
            with self.subTest(dimension=dimension):
                self.record = deepcopy(baseline)
                del self.record["isolation"][dimension]
                with self.assertRaises(delivery.ContractError):
                    self.validate("implement")

    def test_files_cannot_be_not_applicable_and_evidence_cannot_be_empty(self):
        self.ready_to_implement()
        for result in [{"status": "not_applicable", "reason": "none"}, {"status": "verified", "evidence": ""}, {"status": "pending"}]:
            with self.subTest(result=result):
                self.record["isolation"]["files"] = result
                with self.assertRaises(delivery.ContractError):
                    self.validate("implement")

    def test_structural_change_requires_human_decision_fields(self):
        self.ready_to_implement()
        self.synthetic_database_decision()
        valid = deepcopy(self.record["database"]["approval"])
        for key, value in [("decision", "pending"), ("actor_type", "agent"), ("source", ""), ("actor", ""), ("recorded_at", "2026-01-01T12:00:00"), ("recorded_at", None)]:
            with self.subTest(key=key):
                self.record["database"]["approval"] = {**valid, key: value}
                with self.assertRaises(delivery.ContractError):
                    self.validate("implement")
        del self.record["database"]["approval"]
        with self.assertRaises(delivery.ContractError):
            self.validate("implement")

    def test_proposal_edit_invalidates_synthetic_decision(self):
        self.ready_to_implement()
        proposal = self.synthetic_database_decision()
        self.validate("implement")
        proposal.write_text("Proposta alterada após a decisão fictícia.")
        with self.assertRaisesRegex(delivery.ContractError, "versão aprovada"):
            self.validate("implement")

    def test_nonstructural_work_rejects_fabricated_approval(self):
        self.ready_to_implement()
        self.record["database"]["approval"] = {"decision": "approved"}
        with self.assertRaises(delivery.ContractError):
            self.validate("implement")

    def test_complete_declarations_pass_without_proving_their_truth(self):
        self.ready_to_deliver()
        self.validate()

    def test_reviewer_must_not_be_an_implementer(self):
        self.ready_to_deliver()
        for reviewer in ["fixture-developer", " fixture-developer ", ""]:
            with self.subTest(reviewer=reviewer):
                self.record["qa"]["reviewer"] = reviewer
                with self.assertRaises(delivery.ContractError):
                    self.validate()

    def test_qa_requires_all_acceptance_criteria_once_and_passed(self):
        self.ready_to_deliver()
        criteria = deepcopy(self.record["qa"]["criteria"])
        for results in [criteria[:1], [criteria[0], criteria[0]], [*criteria, criteria[0]], [criteria[0], {**criteria[1], "status": "blocked"}]]:
            with self.subTest(results=results):
                self.record["qa"]["criteria"] = results
                with self.assertRaises(delivery.ContractError):
                    self.validate()

    def test_qa_requires_additional_grounded_scenario(self):
        self.ready_to_deliver()
        scenario = deepcopy(self.record["qa"]["additional_scenarios"][0])
        for results in [[], [{**scenario, "basis": ""}], [{**scenario, "expected": ""}], [{**scenario, "status": "failed"}]]:
            with self.subTest(results=results):
                self.record["qa"]["additional_scenarios"] = results
                with self.assertRaises(delivery.ContractError):
                    self.validate()

    def test_failed_checks_and_unowned_integration_block_delivery(self):
        self.ready_to_deliver()
        self.record["checks"][0]["status"] = "failed"
        with self.assertRaises(delivery.ContractError):
            self.validate()
        self.record["checks"][0]["status"] = "passed"
        self.record["integration"]["owner"] = "another-fixture-actor"
        with self.assertRaises(delivery.ContractError):
            self.validate()

    def test_manual_guide_and_pr_draft_are_required(self):
        self.ready_to_deliver()
        for key in ["manual_test", "pr_draft"]:
            with self.subTest(key=key):
                path = self.project / self.record[key]
                path.write_text("")
                with self.assertRaises(delivery.ContractError):
                    self.validate()
                path.write_text("Fixture restored")

    def test_observer_is_not_a_delivery_role(self):
        self.record["roles"] = ["observador-negocio"]
        with self.assertRaises(delivery.ContractError):
            self.validate("plan")

    def test_story_requires_explicit_dependencies_and_unique_criteria(self):
        path = self.project / self.record["story"]
        valid = path.read_text()
        for story in [valid.replace("## Dependências e limites", "## Other"), valid.replace("AC-02:", "AC-01:")]:
            path.write_text(story)
            with self.assertRaises(delivery.ContractError):
                self.validate("plan")

    def test_paths_cannot_escape_project_even_through_symlinks(self):
        with tempfile.TemporaryDirectory() as outside:
            secret = Path(outside) / "private.md"
            secret.write_text("Do not read this content")
            (self.project / "linked.md").symlink_to(secret)
            for value in [str(secret), "linked.md", "../missing.md"]:
                with self.subTest(value=value):
                    self.record["story"] = value
                    with self.assertRaises(delivery.ContractError):
                        self.validate("plan")

    def test_config_requires_disabled_observers_and_schedule_context(self):
        delivery.validate_config(self.config, self.project)
        for name in ["reliability", "business"]:
            config = deepcopy(self.config)
            config["observers"][name]["enabled"] = True
            with self.assertRaises(delivery.ContractError):
                delivery.validate_config(config, self.project)
        self.config["observers"]["business"]["requires_scheduled_activity"] = False
        with self.assertRaises(delivery.ContractError):
            delivery.validate_config(self.config, self.project)

    def test_config_does_not_accept_permission_grants(self):
        self.config["permissions"] = {"push": True}
        with self.assertRaises(delivery.ContractError):
            delivery.validate_config(self.config, self.project)

    def test_cli_reads_without_executing_configured_commands_or_writing_files(self):
        self.ready_to_deliver()
        sentinel = self.project / "SHOULD_NOT_EXIST"
        self.config["checks"]["test"] = [sys.executable, "-c", "from pathlib import Path; Path('SHOULD_NOT_EXIST').touch()"]
        self.write(".bezalel/project.json", json.dumps(self.config))
        self.write(".bezalel/deliveries/US-001.local.json", json.dumps(self.record))
        before = {str(path): path.read_bytes() for path in self.project.rglob("*") if path.is_file()}
        result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/check_delivery.py"), "--project", str(self.project), "--record", ".bezalel/deliveries/US-001.local.json", "--stage", "deliver"], cwd=self.project, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Não comprova", result.stdout)
        self.assertFalse(sentinel.exists())
        self.assertEqual(before, {str(path): path.read_bytes() for path in self.project.rglob("*") if path.is_file()})

    def test_invalid_json_diagnostic_does_not_echo_contents(self):
        path = self.write("invalid.json", "PRIVATE_FIXTURE_VALUE")
        with self.assertRaises(delivery.ContractError) as caught:
            delivery.read_json(path)
        self.assertNotIn("PRIVATE_FIXTURE_VALUE", str(caught.exception))

    def test_package_catalog_and_links_are_consistent(self):
        self.assertEqual(repository.validate_agents(), [])
        self.assertEqual(repository.validate_structure(repository.package_files()), [])

    def test_nine_named_agents_preserve_observation_owners_and_human_boundary(self):
        catalog = delivery.read_json(ROOT / "agents/catalog.json")
        self.assertEqual({entry["display_name"] for entry in catalog["roles"].values()}, {
            "Product Manager", "Tech Lead", "Engenheiro DevOps", "Desenvolvedor fullstack",
            "Desenvolvedor backend", "Desenvolvedor frontend web", "Desenvolvedor mobile",
            "Engenheiro de QA", "Analista de Produto",
        })
        self.assertEqual(len(catalog["roles"]), 9)
        self.assertNotIn("observador-confiabilidade", catalog["roles"])
        self.assertEqual(catalog["responsibilities"]["reliability"]["owner_role"], "infraestrutura")
        self.assertEqual(catalog["responsibilities"]["business"]["owner_role"], "observador-negocio")
        self.assertNotIn("aprovador-humano", catalog["roles"])
        self.record["roles"] = ["aprovador-humano"]
        with self.assertRaises(delivery.ContractError):
            self.validate("plan")

    def test_checker_rejects_active_or_orphaned_observation_responsibility(self):
        baseline = delivery.read_json(ROOT / "agents/catalog.json")
        original_read = repository.read_json
        for key, value in [("enabled", True), ("owner_role", "missing-role")]:
            with self.subTest(key=key):
                catalog = deepcopy(baseline)
                catalog["responsibilities"]["reliability"][key] = value
                with patch.object(repository, "read_json", side_effect=lambda path: catalog if path.name == "catalog.json" else original_read(path)):
                    self.assertTrue(repository.validate_agents())

    def test_checker_rejects_presentation_name_different_from_role_contract(self):
        catalog = delivery.read_json(ROOT / "agents/catalog.json")
        catalog["roles"]["qa"]["display_name"] = "Outro cargo"
        original_read = repository.read_json
        with patch.object(repository, "read_json", side_effect=lambda path: catalog if path.name == "catalog.json" else original_read(path)):
            self.assertTrue(repository.validate_agents())

    def test_malformed_catalog_reports_failure_without_traceback(self):
        self.write("agents/catalog.json", "[]")
        with patch.object(repository, "ROOT", self.project):
            self.assertTrue(repository.validate_agents())
        with patch.object(delivery, "ROOT", self.project):
            with self.assertRaises(delivery.ContractError):
                self.validate("plan")


if __name__ == "__main__":
    unittest.main()
