"""Structural package checks; no workbook calculation or product execution."""
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import check_repository as repository


class TemplateTests(unittest.TestCase):
    def test_packaged_template_passes(self):
        self.assertEqual(repository.validate_workbook_template(), [])

    def test_corruption_and_wrong_sheets_fail(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'fixture.xlsx'
            path.write_text('Not a spreadsheet')
            self.assertTrue(repository.validate_workbook_template(path))
            with zipfile.ZipFile(path, 'w') as archive:
                archive.writestr('xl/workbook.xml', '<workbook/>')
            self.assertTrue(repository.validate_workbook_template(path))

    def test_external_relationship_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'fixture.xlsx'
            source = ROOT / 'skills/development-test-workbook/assets/test-plan-template.xlsx'
            with zipfile.ZipFile(source) as original, zipfile.ZipFile(path, 'w') as target:
                for name in original.namelist():
                    target.writestr(name, original.read(name))
                target.writestr('xl/_rels/fixture.rels', '<Relationships><Relationship TargetMode="External" Target="https://example.invalid"/></Relationships>')
            self.assertTrue(repository.validate_workbook_template(path))
