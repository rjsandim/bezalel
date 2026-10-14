"""Contratos públicos de geração e falhas do pool, sem daemon ou dados reais."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import test_lifecycle as lifecycle

MODULE = Path(__file__).resolve().parents[1] / "scripts/shared_db.py"
spec = importlib.util.spec_from_file_location("shared_db", MODULE)
shared = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared)


class SharedGenerationTests(unittest.TestCase):
    run_process = lifecycle.LifecycleTests.run_process
    command = lifecycle.LifecycleTests.command
    observed = lifecycle.LifecycleTests.observed

    def setUp(self):
        lifecycle.LifecycleTests.setUp(self)
        self.manifest = self.repo / ".envstack/stack.yaml"
        self.manifest.write_text(self.manifest.read_text() + "\ndatabase_mode: shared\ndatabase_shared:\n  pool: mysql-8-4\n  image: mysql:8.4\n  port: 35306\n")
        (self.repo / ".envstack/api.env.example").write_text("\n".join([
            "DB_HOST=${env:db.host}", "DB_PORT=${env:db.port}",
            "DB_DATABASE=${env:db.db}", "DB_USERNAME=${env:db.user}",
            "DB_PASSWORD=${env:db.password}", "LOCAL_SETTING=preserve",
        ]) + "\n")
        self.command("new.sh", "shared", extra={"ENV_DRY_RUN": "1"})
        self.directory = self.skill / "state/fixture/shared"
        self.metadata = json.loads((self.directory / shared.STATE_FILE).read_text())

    def config(self):
        return json.loads((self.directory / "docker-compose.yml").read_text())

    def test_database_outside_environment_and_redis_stays_local(self):
        config = self.config()
        self.assertNotIn("mysql", config["services"])
        self.assertIn("redis", config["services"])
        self.assertEqual(config["volumes"], {})
        self.assertTrue(config["networks"]["shared-database"]["external"])
        self.assertNotIn("mysql", config["services"]["api"]["depends_on"])
        self.assertIn("shared-database", config["services"]["api"]["networks"])
        self.assertNotIn("shared-database", config["services"]["docs"]["networks"])
        connection = self.metadata["connections"]["api"]
        self.assertNotIn(connection["password"], json.dumps(config))
        envfile = self.repo / ".worktrees/shared/api/.env"
        self.assertEqual(envfile.stat().st_mode & 0o777, 0o600)
        self.assertIn("DB_DATABASE=" + connection["db"], envfile.read_text())
        ide = self.repo / ".worktrees/shared/.idea/dataSources.xml"
        self.assertIn(":35306/" + connection["db"], ide.read_text())

    def test_two_environments_share_server_but_not_names_or_credentials(self):
        self.command("new.sh", "second", extra={"ENV_DRY_RUN": "1"})
        other = json.loads((self.skill / "state/fixture/second" / shared.STATE_FILE).read_text())
        self.assertEqual(self.metadata["pool"], other["pool"])
        for field in ("db", "user", "password"):
            self.assertNotEqual(self.metadata["connections"]["api"][field], other["connections"]["api"][field])
        self.assertNotIn("_", other["connections"]["api"]["db"])

    def test_update_preserves_private_identity_and_local_edits(self):
        envfile = self.repo / ".worktrees/shared/api/.env"
        envfile.write_text(envfile.read_text() + "CUSTOM_VALUE=untouched\n")
        before = envfile.read_bytes()
        metadata = (self.directory / shared.STATE_FILE).read_bytes()
        self.command("update.sh", "shared", extra={"ENV_DRY_RUN": "1"})
        self.assertEqual(before, envfile.read_bytes())
        self.assertEqual(metadata, (self.directory / shared.STATE_FILE).read_bytes())

    def test_existing_isolated_environment_requires_migration(self):
        before = self.compose.read_bytes()
        result = self.command("update.sh", "check", extra={"ENV_DRY_RUN": "1"}, expected=1)
        self.assertIn("migração explícita", result.stderr)
        self.assertEqual(before, self.compose.read_bytes())
        self.assertFalse((self.compose.parent / shared.STATE_FILE).exists())

    def test_invalid_pool_config_can_be_corrected_without_orphaning_state(self):
        original = self.manifest.read_text()
        self.manifest.write_text(original.replace("image: mysql:8.4", "image: mysql:latest"))
        self.command("new.sh", "retry", extra={"ENV_DRY_RUN": "1"}, expected=1)
        self.manifest.write_text(original)
        self.command("new.sh", "retry", extra={"ENV_DRY_RUN": "1"})
        self.assertTrue((self.skill / "state/fixture/retry/docker-compose.yml").exists())

    def test_pool_version_change_rejected_before_compose_replacement(self):
        before = (self.directory / "docker-compose.yml").read_bytes()
        self.manifest.write_text(self.manifest.read_text().replace("image: mysql:8.4", "image: mysql:9.0"))
        self.command("update.sh", "shared", extra={"ENV_DRY_RUN": "1"}, expected=1)
        self.assertEqual(before, (self.directory / "docker-compose.yml").read_bytes())

    def test_migration_accepts_legacy_compose_without_startup_metadata(self):
        self.command("update.sh", "check", extra={"ENV_DRY_RUN": "1", "ENV_DATABASE_MIGRATION": "fixture/check"})
        config = json.loads(self.compose.read_text())
        config.pop("x-envstack")
        self.compose.write_text(json.dumps(config))
        self.run_process(["python3", str(self.skill / "scripts/shared_db.py"), "configure", str(self.compose), str(self.compose.parent)], env={**self.env, "DOCKER_CONTEXT": "fixture"})
        self.assertTrue(json.loads(self.compose.read_text())["x-envstack"]["shared_database"])

    def test_docs_only_does_not_start_shared_server(self):
        self.command("ctl.sh", "ensure", "shared", "docs")
        self.assertEqual(self.observed()["running"], ["docs"])
        self.assertFalse(any("_databases" in " ".join(call) for call in self.observed()["calls"]))

    def test_stop_and_restart_do_not_include_pool_server(self):
        self.command("ctl.sh", "start", "shared", "docs")
        before = len(self.observed()["calls"])
        self.command("ctl.sh", "restart", "shared")
        self.command("ctl.sh", "stop", "shared")
        operations = self.observed()["calls"][before:]
        self.assertFalse(any("_databases" in " ".join(call) for call in operations))
        self.assertEqual(self.observed()["running"], [])

    def test_new_env_overrides_legacy_literal_connection_without_touching_example(self):
        example = self.repo / ".envstack/api.env.example"
        text = "DB_HOST=old-host\nDB_PASSWORD=legacy-private-value\nUNRELATED=keep\n"
        example.write_text(text)
        self.command("new.sh", "literal", extra={"ENV_DRY_RUN": "1"})
        actual = (self.repo / ".worktrees/literal/api/.env").read_text()
        self.assertNotIn("old-host", actual)
        self.assertNotIn("legacy-private-value", actual)
        self.assertIn("UNRELATED=keep", actual)
        self.assertEqual(example.read_text(), text)

    def test_shared_destroy_preserves_registered_database_credentials(self):
        pool = self.skill / "state/_databases/fixture/mysql-8-4"
        credential = (pool / "admin.env").read_bytes()
        self.command("destroy.sh", "shared", "--confirm", "fixture/shared", "--keep-worktree")
        self.assertEqual(credential, (pool / "admin.env").read_bytes())
        self.assertFalse(any(call[:2] == ["docker", "exec"] for call in self.observed()["calls"]))

    def test_postgres_generation_and_real_compose_validation_without_daemon(self):
        self.manifest.write_text(self.manifest.read_text().replace("mysql", "postgres").replace("8-4", "17").replace("8.4", "17").replace("35306", "35432"))
        self.command("new.sh", "pg", extra={"ENV_DRY_RUN": "1"})
        pool_compose = self.skill / "state/_databases/fixture/postgres-17/compose.json"
        self.run_process([lifecycle.DOCKER, "compose", "-f", str(pool_compose), "config", "--quiet"])
        self.assertIn("DB_CONNECTION=pgsql", (self.repo / ".worktrees/pg/api/.env").read_text())

    def test_connection_drift_blocks_pool_start_without_exposing_secret(self):
        envfile = self.repo / ".worktrees/shared/api/.env"
        envfile.write_text("DB_PASSWORD=private-test-value\n")
        result = self.command("ctl.sh", "ensure", "shared", "api", expected=1)
        self.assertIn("diverge", result.stderr)
        self.assertNotIn("private-test-value", result.stderr + result.stdout)
        self.assertFalse(any("up" in call for call in self.observed()["calls"]))


class PoolTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.skill = Path(self.tmp.name)
        self.addCleanup(patch.stopall)
        patch.object(shared, "SKILL", self.skill).start()
        patch.dict(os.environ, DOCKER_CONTEXT="fixture", ENV_ALLOW_SHARED_INFRA="1").start()
        import shutil
        shutil.copytree(MODULE.parents[1] / "templates", self.skill / "templates")
        self.pool = shared.pool_spec(dict(database="mysql", database_shared=dict(pool="mysql-8-4", image="mysql:8.4", port=35306)), "fixture")
        shared.save_pool(self.pool)
        self.state = self.skill / "state/example/feature"
        self.connection = dict(db="esexamplefeatureapi123", user="es01234567", password="ab1234", host=self.pool["hostname"], port="3306", env_fields={"url": "DATABASE_URL"})
        self.data = dict(owner=dict(root=str(self.skill), project="example", environment="feature"), pool=self.pool, connections=dict(api=self.connection))
        shared.write_private(self.state / shared.STATE_FILE, self.data)
        envfile = self.skill / ".worktrees/feature/api/.env"
        shared.write_private(envfile, "DATABASE_URL=" + shared.connection_values(self.connection, "mysql")["url"] + "\n")
        self.compose = self.state / "compose.json"
        shared.write_private(self.compose, dict(services=dict(api={})))
        self.calls = []
        self.count = 0

        def fake_run(*args, input=None):
            self.calls.append((args, input))
            if args[0] == "yq":
                return self.compose.read_text()
            if args[1:3] == ("volume", "ls"):
                return self.pool["volume"]
            if args[1:3] == ("volume", "inspect"):
                return json.dumps({"com.docker.compose.project": self.pool["compose_project"]})
            if args[1] in ("network", "ps", "compose"):
                return ""
            if args[1] == "exec":
                if "COUNT(*)" in (input or ""):
                    return str(self.count)
                if "CREATE DATABASE" in (input or ""):
                    self.count = 2
                    return ""
                if "login-check" in args:
                    return "1"
            raise AssertionError(args)
        patch.object(shared, "run", side_effect=fake_run).start()

    def ensure(self):
        shared.ensure(str(self.state), str(self.compose), ["api"])

    def test_idempotent_start_provisions_once_and_checks_login(self):
        self.ensure()
        self.ensure()
        writes = [data for _, data in self.calls if data and "CREATE DATABASE" in data]
        self.assertEqual(len(writes), 1)
        self.assertEqual(sum("login-check" in args for args, _ in self.calls), 2)
        self.assertFalse(any(self.connection["password"] in " ".join(args) for args, _ in self.calls))

    def test_unowned_database_is_never_adopted(self):
        self.count = 2
        with self.assertRaisesRegex(shared.SharedDatabaseError, "sem vínculo"):
            self.ensure()
        self.assertFalse(any(data and "GRANT" in data for _, data in self.calls))

    def test_missing_previously_provisioned_database_is_not_recreated(self):
        self.ensure()
        self.calls.clear()
        self.count = 1
        with self.assertRaisesRegex(shared.SharedDatabaseError, "ausente"):
            self.ensure()
        self.assertFalse(any(data and "CREATE DATABASE" in data for _, data in self.calls))

    def test_sql_failure_keeps_pending_record_and_retry_can_finish(self):
        with patch.object(shared, "provision", side_effect=shared.SharedDatabaseError("SQL indisponível")):
            with self.assertRaises(shared.SharedDatabaseError):
                self.ensure()
        members = list((shared.pool_dir(self.pool) / "members").glob("*.json"))
        self.assertEqual(shared.read_json(members[0])["status"], "pending")
        self.ensure()
        self.assertEqual(shared.read_json(members[0])["status"], "ready")

    def test_foreign_volume_blocks_start(self):
        with patch.object(shared, "verify_resources", side_effect=shared.SharedDatabaseError("Recurso sem propriedade")):
            with self.assertRaises(shared.SharedDatabaseError):
                self.ensure()
        self.assertFalse(any("up" in args for args, _ in self.calls))

    def test_pool_port_conflict_and_version_mismatch_preserve_original(self):
        original = (shared.pool_dir(self.pool) / "admin.env").read_bytes()
        changed = dict(self.pool, image="mysql:9.0")
        with self.assertRaises(shared.SharedDatabaseError):
            shared.save_pool(changed)
        with self.assertRaises(shared.SharedDatabaseError):
            shared.save_pool(dict(self.pool, pool="another"))
        self.assertEqual(original, (shared.pool_dir(self.pool) / "admin.env").read_bytes())

    def test_postgres_uses_restricted_owner_and_separate_database(self):
        statements = []
        with patch.object(shared, "sql", side_effect=lambda spec, statement: statements.append(statement)):
            shared.provision(dict(self.pool, engine="postgres"), self.connection)
        self.assertIn("NOSUPERUSER NOCREATEDB NOCREATEROLE", statements[0])
        self.assertIn("REVOKE ALL ON DATABASE", statements[0])
        self.assertIn("OWNER " + self.connection["user"], statements[0])
        self.assertNotIn("CREATE SCHEMA", statements[0])


if __name__ == "__main__":
    unittest.main()
