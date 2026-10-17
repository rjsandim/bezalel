"""Exceção de formato não dispensa identidade nem integridade dos links."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import check_repository as repository


class ExternalSkillStructureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.root_patch = patch.object(repository, "ROOT", self.root)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)

    def skill(self, directory, name=None, body="## Upstream section\n"):
        path = self.root / "skills" / directory / "SKILL.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"---\nname: {name or directory}\ndescription: Synthetic fixture\n---\n{body}"
        )
        return path

    def test_only_declared_external_skill_preserves_upstream_format(self):
        external = self.skill("security-audit")
        self.assertEqual(repository.validate_structure([external]), [])
        local = self.skill("local-skill")
        self.assertEqual(
            repository.validate_structure([external, local]),
            ["Unexpected section order: local-skill"],
        )

    def test_external_skill_still_requires_matching_identity_and_valid_links(self):
        external = self.skill(
            "security-audit", name="wrong-name",
            body="## Upstream section\n[Missing](references/missing.md)\n",
        )
        errors = repository.validate_structure([external])
        self.assertIn("Invalid essential metadata: security-audit", errors)
        self.assertTrue(any("Missing/outside link" in error for error in errors))

    def test_imported_skills_accept_block_descriptions_without_rewriting_them(self):
        for marker in ("|", "|-", ">", ">+"):
            with self.subTest(marker=marker):
                external = self.skill("humanizer")
                external.write_text(
                    "---\nname: humanizer\ndescription: " + marker
                    + "\n  Preserve the original meaning.\n"
                    + "  Edit only prose.\nlicense: MIT\n---\n## Upstream section\n"
                )
                original = external.read_bytes()
                self.assertEqual(repository.validate_structure([external]), [])
                self.assertEqual(external.read_bytes(), original)

    def test_empty_block_or_scalar_description_is_not_valid_metadata(self):
        for description in ("|\nlicense: MIT", ">-\n  # comment only", "''", '\"\"', " "):
            with self.subTest(description=description):
                external = self.skill("humanizer")
                external.write_text(
                    "---\nname: humanizer\ndescription: " + description
                    + "\n---\n## Upstream section\n"
                )
                self.assertIn(
                    "Invalid essential metadata: humanizer",
                    repository.validate_structure([external]),
                )

    def test_new_format_exceptions_keep_identity_and_link_checks(self):
        for name in (
            "humanizer", "verification-planning", "agent-browser", "release",
            "reflect", "github-resolution", "pr-bump", "pr-post-audit",
        ):
            with self.subTest(name=name):
                external = self.skill(
                    name, name="wrong-name",
                    body="## Upstream section\n[Missing](references/missing.md)\n",
                )
                errors = repository.validate_structure([external])
                self.assertIn("Invalid essential metadata: " + name, errors)
                self.assertTrue(any("Missing/outside link" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
