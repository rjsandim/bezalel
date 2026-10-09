"""Offline tests with synthetic inputs; no real credentials or network access."""

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    "check_config", Path(__file__).parents[1] / "scripts/check_config.py"
)
config = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(config)
SYNTHETIC_ENV = {"COOLIFY_API_TOKEN": "TEST_ONLY_NOT_A_CREDENTIAL"}


class ProjectConfigTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name) / "project-a"
        (self.project / ".bezalel").mkdir(parents=True)
        self.path = self.project / ".bezalel/vps-deploy.local.json"
        self.write_config()

    def write_config(self, **overrides):
        data = {"coolify_base_url": "https://coolify.test", "ssh_target": ""}
        data.update(overrides)
        self.path.write_text(json.dumps(data))

    def test_valid_config_only_reads_and_does_not_connect(self):
        before = self.path.read_bytes()
        with patch("socket.socket", side_effect=AssertionError("Network forbidden")):
            config.validate_project(self.project, SYNTHETIC_ENV)
        self.assertEqual(before, self.path.read_bytes())

    def test_second_project_never_falls_back_to_first(self):
        other = Path(self.temp.name) / "project-b"
        other.mkdir()
        config.validate_project(self.project, SYNTHETIC_ENV)
        with self.assertRaisesRegex(config.ConfigError, "Falta"):
            config.validate_project(other, SYNTHETIC_ENV)

    def test_empty_token_fails_without_creating_config(self):
        before = self.path.read_bytes()
        for environment in [{}, {"COOLIFY_API_TOKEN": "   "}]:
            with self.subTest(environment=bool(environment)):
                with self.assertRaisesRegex(config.ConfigError, "ausente"):
                    config.validate_project(self.project, environment)
        self.assertEqual(before, self.path.read_bytes())

    def test_secret_field_is_rejected_without_echo(self):
        sentinel = "SYNTHETIC_SECRET_DO_NOT_PRINT"
        self.write_config(token=sentinel)
        error_output = io.StringIO()
        with contextlib.redirect_stderr(error_output):
            result = config.main(["--project", str(self.project)])
        self.assertEqual(1, result)
        self.assertNotIn(sentinel, error_output.getvalue())

    def test_malformed_json_does_not_echo_contents(self):
        sentinel = "SYNTHETIC_PRIVATE_CONTENT"
        self.path.write_text(sentinel)
        with self.assertRaises(config.ConfigError) as error:
            config.validate_project(self.project, SYNTHETIC_ENV)
        self.assertNotIn(sentinel, str(error.exception))

    def test_unsafe_urls_and_placeholder_are_rejected(self):
        for url in [
            "http://remote.test", "https://user:TEST_ONLY@coolify.test",
            "https://coolify.test/?token=TEST_ONLY", "https://coolify.test/#token",
            "https://coolify.example.invalid", "https://coolify.test:bad",
            "file:///local", "https://coolify.test\n", "https://example.com",
        ]:
            with self.subTest(url=url):
                self.write_config(coolify_base_url=url)
                with self.assertRaises(config.ConfigError):
                    config.validate_project(self.project, SYNTHETIC_ENV)

    def test_http_is_allowed_only_for_local_access(self):
        for url in ["http://localhost:8000", "http://127.0.0.1:8000", "http://[::1]:8000"]:
            with self.subTest(url=url):
                self.write_config(coolify_base_url=url)
                config.validate_project(self.project, SYNTHETIC_ENV)

    def test_token_control_characters_are_rejected_without_echo(self):
        with self.assertRaises(config.ConfigError) as error:
            config.validate_project(self.project, {"COOLIFY_API_TOKEN": "TEST_ONLY\nHEADER"})
        self.assertNotIn("TEST_ONLY", str(error.exception))

    def test_ssh_options_cannot_be_mistaken_for_target(self):
        for target in ["-oProxyCommand=command", "host;command", "user@host other"]:
            self.write_config(ssh_target=target)
            with self.assertRaises(config.ConfigError):
                config.validate_project(self.project, SYNTHETIC_ENV)

    def test_shared_symlink_config_is_rejected(self):
        original = self.path.with_name("shared.json")
        self.path.rename(original)
        self.path.symlink_to(original)
        with self.assertRaisesRegex(config.ConfigError, "symlink"):
            config.validate_project(self.project, SYNTHETIC_ENV)


if __name__ == "__main__":
    unittest.main()
