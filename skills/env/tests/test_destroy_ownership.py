"""Ownership decisions tested with Docker output fixtures only."""
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('check_destroy', Path(__file__).parents[1] / 'scripts/check_destroy.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class OwnershipTests(unittest.TestCase):
    def test_volume_owned_by_another_project_is_preserved(self):
        outputs = [json.dumps({'name': 'fixture', 'volumes': {'db': {'name': 'shared'}}}), 'shared\n', json.dumps({'com.docker.compose.project': 'another'})]
        with patch.object(checker, 'docker_output', side_effect=outputs):
            with self.assertRaises(ValueError):
                checker.check('fixture.yml', 'fixture')

    def test_wrong_compose_project_fails_before_other_inspection(self):
        with patch.object(checker, 'docker_output', return_value='{"name":"another"}') as read:
            with self.assertRaises(ValueError):
                checker.check('fixture.yml', 'fixture')
            self.assertEqual(read.call_count, 1)

    def test_external_volume_is_not_in_deletion_set(self):
        outputs = [json.dumps({'name': 'fixture', 'volumes': {'db': {'name': 'shared', 'external': True}}}), 'shared\n', 'other\n', json.dumps({'project': 'other', 'mounts': [{'Name': 'shared'}]})]
        with patch.object(checker, 'docker_output', side_effect=outputs):
            checker.check('fixture.yml', 'fixture')
