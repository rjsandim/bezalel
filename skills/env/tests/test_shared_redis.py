"""Geração e falhas do Redis compartilhado com processos simulados."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

import test_lifecycle as lifecycle

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import shared_redis as shared


class RedisGenerationTests(unittest.TestCase):
    run_process = lifecycle.LifecycleTests.run_process
    command = lifecycle.LifecycleTests.command
    observed = lifecycle.LifecycleTests.observed

    def setUp(self):
        lifecycle.LifecycleTests.setUp(self)
        self.manifest = self.repo / ".envstack/stack.yaml"
        content = self.manifest.read_text().replace("folder: api,", "folder: api, redis: true,")
        self.manifest.write_text(content + "\nredis_mode: shared\nredis_shared:\n  pool: redis-7-4\n  image: redis:7.4-alpine\n  port: 35379\n  databases: 8\n")
        self.command("new.sh", "shared", extra={"ENV_DRY_RUN": "1"})
        self.directory = self.skill / "state/fixture/shared"
        self.metadata = json.loads((self.directory / shared.STATE_FILE).read_text())

    def test_shared_network_only_for_consumers_and_no_local_redis(self):
        config = json.loads((self.directory / "docker-compose.yml").read_text())
        self.assertNotIn("redis", config["services"])
        self.assertIn("mysql", config["services"])
        self.assertNotIn("redis", config["services"]["api"]["depends_on"])
        self.assertIn("shared-redis", config["services"]["api"]["networks"])
        self.assertNotIn("shared-redis", config["services"]["docs"]["networks"])
        self.assertTrue(config["networks"]["shared-redis"]["external"])
        self.assertNotIn(self.metadata["connections"]["api"]["password"], json.dumps(config))

    def test_generated_env_includes_authentication_distinct_databases_and_prefix(self):
        envfile = self.repo / ".worktrees/shared/api/.env"
        values = dict(line.split("=", 1) for line in envfile.read_text().splitlines())
        connection = self.metadata["connections"]["api"]
        for field, variable in shared.FIELDS.items():
            self.assertEqual(values[variable], connection[field])
        self.assertNotEqual(values["REDIS_DB"], values["REDIS_CACHE_DB"])
        self.assertNotIn("0", [values["REDIS_DB"], values["REDIS_CACHE_DB"]])
        self.assertEqual(envfile.stat().st_mode & 0o777, 0o600)

    def test_allocations_are_exclusive_and_never_reused_after_destroy(self):
        self.command("new.sh", "other", extra={"ENV_DRY_RUN": "1"})
        other = json.loads((self.skill / "state/fixture/other" / shared.STATE_FILE).read_text())
        first, second = self.metadata["connections"]["api"], other["connections"]["api"]
        self.assertTrue({first["db"], first["cache_db"]}.isdisjoint({second["db"], second["cache_db"]}))
        for key in ("prefix", "user", "password"):
            self.assertNotEqual(first[key], second[key])
        pool = self.skill / "state/_redis/fixture/redis-7-4"
        before = (pool / "allocations.json").read_bytes()
        self.command("destroy.sh", "shared", "--confirm", "fixture/shared", "--keep-worktree")
        self.assertEqual(before, (pool / "allocations.json").read_bytes())
        self.assertFalse(any("exec" in call for call in self.observed()["calls"]))
        self.command("new.sh", "third", extra={"ENV_DRY_RUN": "1"})
        third = json.loads((self.skill / "state/fixture/third" / shared.STATE_FILE).read_text())
        self.assertTrue({first["db"], first["cache_db"]}.isdisjoint({third["connections"]["api"]["db"], third["connections"]["api"]["cache_db"]}))

    def test_update_preserves_env_and_private_credentials(self):
        path = self.repo / ".worktrees/shared/api/.env"
        path.write_text(path.read_text() + "CUSTOM=keep\n")
        before = path.read_bytes()
        metadata = (self.directory / shared.STATE_FILE).read_bytes()
        self.command("update.sh", "shared", extra={"ENV_DRY_RUN": "1"})
        self.assertEqual(before, path.read_bytes())
        self.assertEqual(metadata, (self.directory / shared.STATE_FILE).read_bytes())

    def test_existing_environment_cannot_silently_switch_redis(self):
        before = self.compose.read_bytes()
        result = self.command("update.sh", "check", extra={"ENV_DRY_RUN": "1"}, expected=1)
        self.assertIn("migração explícita", result.stderr)
        self.assertEqual(before, self.compose.read_bytes())

    def test_legacy_url_does_not_override_laravel_cache_database(self):
        example = self.repo / ".envstack/api.env.example"
        example.write_text("REDIS_HOST=old\nREDIS_URL=redis://old/0\nLOCAL=keep\n")
        self.command("new.sh", "url", extra={"ENV_DRY_RUN": "1"})
        values = dict(line.split("=", 1) for line in (self.repo / ".worktrees/url/api/.env").read_text().splitlines())
        self.assertEqual(values["LOCAL"], "keep")
        self.assertTrue(values["REDIS_URL"].endswith(":6379"))
        self.assertNotEqual(values["REDIS_DB"], values["REDIS_CACHE_DB"])
        self.assertIn("REDIS_HOST=old", example.read_text())

    def test_docs_only_does_not_start_pool_and_lifecycle_excludes_it(self):
        self.command("ctl.sh", "start", "shared", "docs")
        self.command("ctl.sh", "restart", "shared")
        self.command("ctl.sh", "stop", "shared")
        self.assertFalse(any("_redis" in " ".join(call) for call in self.observed()["calls"]))

    def test_pool_compose_is_valid_without_daemon(self):
        compose = self.skill / "state/_redis/fixture/redis-7-4/compose.json"
        self.run_process([lifecycle.DOCKER, "compose", "-f", str(compose), "config", "--quiet"])
        config = json.loads(compose.read_text())
        self.assertEqual(config["services"]["redis"]["ports"], ["127.0.0.1:35379:6379"])

    def test_pool_capacity_exhaustion_does_not_reuse_indices(self):
        self.command("new.sh", "second", extra={"ENV_DRY_RUN": "1"})
        self.command("new.sh", "third", extra={"ENV_DRY_RUN": "1"})
        result = self.command("new.sh", "fourth", extra={"ENV_DRY_RUN": "1"}, expected=1)
        self.assertIn("sem pares livres", result.stderr)

    def test_context_and_env_drift_block_before_start(self):
        path = self.repo / ".worktrees/shared/api/.env"
        path.write_text("REDIS_PASSWORD=private-test-value\n")
        result = self.command("ctl.sh", "ensure", "shared", "api", expected=1)
        self.assertIn("diverge", result.stderr)
        self.assertNotIn("private-test-value", result.stdout + result.stderr)
        self.assertFalse(any("up" in call for call in self.observed()["calls"]))

    def test_mysql_and_redis_shared_can_be_combined(self):
        self.manifest.write_text(self.manifest.read_text() + "\ndatabase_mode: shared\ndatabase_shared:\n  pool: mysql-8-4\n  image: mysql:8.4\n  port: 35306\n")
        self.command("new.sh", "both", extra={"ENV_DRY_RUN": "1"})
        config = json.loads((self.skill / "state/fixture/both/docker-compose.yml").read_text())
        self.assertNotIn("redis", config["services"])
        self.assertNotIn("mysql", config["services"])
        self.assertTrue({"shared-database", "shared-redis"}.issubset(config["services"]["api"]["networks"]))


class RedisPoolTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.skill = Path(self.tmp.name)
        self.addCleanup(patch.stopall)
        patch.object(shared, "SKILL", self.skill).start()
        shutil.copytree(SCRIPTS.parent / "templates", self.skill / "templates")
        self.spec = shared.pool_spec(dict(redis_shared=dict(pool="redis-7-4", image="redis:7.4-alpine", port=35379)), "fixture")
        shared.save_pool(self.spec)
        self.connection = dict(host=self.spec["hostname"], port="6379", user="es" + "a" * 28,
            password="b" * 48, db="1", cache_db="2", prefix="es:" + "c" * 32 + ":", env_fields=shared.FIELDS)

    def test_redis_major_and_latest_are_not_silently_accepted(self):
        for image in ("redis:latest", "redis:8.0-alpine", "redis:7-alpine"):
            with self.assertRaises(shared.Error):
                shared.pool_spec(dict(redis_shared=dict(pool="redis", image=image, port=35379)), "fixture")

    def test_permission_validation_rejects_cross_database_access(self):
        with patch.object(shared, "commands", return_value=["OK"] * 15):
            with self.assertRaisesRegex(shared.Error, "Permissões"):
                shared.verify_permissions(self.spec, self.connection)

    def test_credentials_never_in_command_arguments_or_errors(self):
        with patch.object(shared, "run", return_value='error:"private-test-value"\n') as execute:
            with self.assertRaises(shared.Error) as error:
                shared.commands(self.spec, [["PING"]], self.connection)
        self.assertNotIn(self.connection["password"], " ".join(execute.call_args.args))
        self.assertNotIn("private-test-value", str(error.exception))

    def test_existing_pool_cannot_change_configuration_or_lose_credentials(self):
        changed = dict(self.spec, port=35380)
        with self.assertRaises(shared.Error):
            shared.save_pool(changed)
        (shared.pool_dir(self.spec) / "admin.env").unlink()
        with self.assertRaises(shared.Error):
            shared.save_pool(self.spec)

    def test_other_database_pool_port_cannot_be_adopted(self):
        path = self.skill / "state/_databases/fixture/another/pool.json"
        shared.write_private(path, {"port": 35432})
        with self.assertRaises(shared.Error):
            shared.save_pool(dict(self.spec, pool="other", port=35432))

    def test_user_cannot_be_allocated_default_database(self):
        with self.assertRaises(shared.Error):
            shared.acl_rules(dict(self.connection, db="0"))

    def test_initialized_pool_missing_volume_blocks_recreation(self):
        shared.write_private(shared.pool_dir(self.spec) / "initialized", "1\n")
        with patch.object(shared, "run", return_value="") as execute:
            with self.assertRaisesRegex(shared.Error, "Volume"):
                shared.verify_resources(self.spec)
        self.assertFalse(any("up" in call.args for call in execute.call_args_list))


if __name__ == "__main__":
    unittest.main()
