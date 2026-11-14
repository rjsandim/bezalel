"""Imagem PostgreSQL e arquivos por worktree, sem infraestrutura real."""
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import test_lifecycle as lifecycle

spec = importlib.util.spec_from_file_location("postgres_shared", lifecycle.SKILL / "scripts/shared_db.py")
shared = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared)


class PostgresImageTests(unittest.TestCase):
    def test_allowlist_and_major_for_both_formats(self):
        for image, major in [("postgres:17", 17), ("postgres:16.4-alpine", 16),
                             ("postgres:18.1", 18), ("pgvector/pgvector:pg17", 17),
                             ("pgvector/pgvector:pg18.1", 18)]:
            with self.subTest(image=image):
                self.assertEqual(shared.postgres_major(image), major)
                pool = shared.pool_spec(dict(database="postgres", database_shared=dict(
                    pool="vector", image=image, port=35432)), "fixture")
                self.assertEqual(pool["image"], image)

    def test_images_outside_allowlist_are_rejected(self):
        for image in ["postgres", "postgres:latest", "pgvector/pgvector:latest",
                      "pgvector/pgvector:pg", "pgvector/pgvector:17", "other/postgres:17",
                      "postgres:17-bookworm", "pgvector/pgvector:pg17-alpine",
                      "mysql:8.4", "postgres:17@sha256:abc", "postgres:17\n"]:
            with self.subTest(image=image), self.assertRaises(shared.SharedDatabaseError):
                shared.pool_spec(dict(database="postgres", database_shared=dict(
                    pool="vector", image=image, port=35432)), "fixture")

    def test_pgvector_does_not_expand_mysql_allowlist(self):
        with self.assertRaises(shared.SharedDatabaseError):
            shared.pool_spec(dict(database="mysql", database_shared=dict(
                pool="mysql", image="pgvector/pgvector:pg17", port=35306)), "fixture")

    def test_container_image_mismatch_is_still_rejected(self):
        pool = shared.pool_spec(dict(database="postgres", database_shared=dict(
            pool="vector", image="pgvector/pgvector:pg17", port=35432)), "fixture")

        def docker(*args):
            if args[1] in ("volume", "network"):
                return ""
            if args[1] == "ps":
                return pool["hostname"]
            if args[1] == "inspect":
                return json.dumps(dict(Image="postgres:17", Labels={
                    "com.docker.compose.project": pool["compose_project"]}))
            raise AssertionError(args)

        with patch.object(shared, "run", side_effect=docker):
            with self.assertRaisesRegex(shared.SharedDatabaseError, "imagem divergente"):
                shared.verify_resources(pool)


class PostgresGenerationTests(unittest.TestCase):
    run_process = lifecycle.LifecycleTests.run_process
    command = lifecycle.LifecycleTests.command

    def setUp(self):
        lifecycle.LifecycleTests.setUp(self)
        self.manifest = self.repo / ".envstack/stack.yaml"
        self.original = self.manifest.read_text().replace("database: mysql", "database: postgres")

    def test_isolated_image_default_official_and_pgvector(self):
        for name, image, mount in [("default", None, "/var/lib/postgresql/data"),
                                   ("official", "postgres:16.4-alpine", "/var/lib/postgresql/data"),
                                   ("vector", "pgvector/pgvector:pg17", "/var/lib/postgresql/data"),
                                   ("vector-next", "pgvector/pgvector:pg18", "/var/lib/postgresql")]:
            with self.subTest(image=image):
                self.manifest.write_text(self.original + (f"\ndatabase_image: {image}\n" if image else ""))
                self.command("new.sh", name, extra={"ENV_DRY_RUN": "1"})
                compose = self.skill / f"state/fixture/{name}/docker-compose.yml"
                result = self.run_process([lifecycle.DOCKER, "compose", "-f", str(compose), "config", "--format", "json"])
                service = json.loads(result.stdout)["services"]["postgres"]
                self.assertEqual(service["image"], image or "postgres:17")
                self.assertIn(mount, [v["target"] for v in service["volumes"]])

    def test_invalid_isolated_image_fails_before_state_or_worktree_creation(self):
        for image in ("other/postgres:17", "postgres:latest", "pgvector/pgvector:latest"):
            with self.subTest(image=image):
                self.manifest.write_text(self.original + f"\ndatabase_image: {image}\n")
                self.command("new.sh", "invalid", extra={"ENV_DRY_RUN": "1"}, expected=1)
                self.assertFalse((self.repo / ".worktrees/invalid").exists())
                self.assertFalse((self.skill / "state/fixture/invalid").exists())


class WorktreeManifestTests(unittest.TestCase):
    run_process = lifecycle.LifecycleTests.run_process
    command = lifecycle.LifecycleTests.command

    def setUp(self):
        lifecycle.LifecycleTests.setUp(self)
        self.main = self.repo
        linked = self.base / "linked"
        self.run_process(["git", "worktree", "add", "-b", "linked", str(linked)])
        self.repo = linked
        self.manifest = linked / ".envstack/stack.yaml"
        self.manifest.write_text(self.manifest.read_text().replace("database: mysql", "database: postgres") +
                                 "\ndatabase_image: pgvector/pgvector:pg17\n")
        # O manifesto sujo do dono não pode ser usado como fonte ou sobrescrito.
        (self.main / ".envstack/stack.yaml").write_text("invalid: [owner work in progress\n")
        (self.main / ".gitignore").write_text("# owner custom rules\n")
        self.before = self.main_snapshot()

    def main_snapshot(self):
        return {str(path.relative_to(self.main)): (path.read_bytes(), path.stat().st_mtime_ns)
                for path in self.main.rglob("*")
                if path.is_file() and path.relative_to(self.main).parts[0] != ".git"}

    def test_init_from_subdirectory_materializes_only_current_worktree(self):
        self.repo = self.repo / "api"
        self.command("init.sh")
        self.repo = self.repo.parent
        self.assertTrue((self.repo / ".envstack/boot.sh").is_file())
        self.assertIn(".worktrees/", (self.repo / ".gitignore").read_text())
        self.assertEqual(self.manifest.read_text().splitlines()[-1], "database_image: pgvector/pgvector:pg17")
        self.assertEqual(self.main_snapshot(), self.before)

    def test_ensure_reads_worktree_manifest_and_keeps_main_files_untouched(self):
        self.command("ctl.sh", "ensure", "local", extra={"ENV_DRY_RUN": "1"})
        state = self.skill / "state/fixture/local"
        self.assertEqual((state / "project-root").read_text().strip(), str(self.repo.resolve()))
        compose = state / "docker-compose.yml"
        result = self.run_process([lifecycle.DOCKER, "compose", "-f", str(compose), "config", "--format", "json"])
        self.assertEqual(json.loads(result.stdout)["services"]["postgres"]["image"], "pgvector/pgvector:pg17")
        self.assertTrue((self.repo / ".worktrees/local/api/.env").is_file())
        self.command("update.sh", "local", extra={"ENV_DRY_RUN": "1"})
        self.command("ctl.sh", "status", "local", "--json", expected=5)
        self.assertEqual(self.main_snapshot(), self.before)

    def test_existing_state_from_other_root_is_not_adopted(self):
        before = {p.name: p.read_bytes() for p in self.compose.parent.iterdir() if p.is_file()}
        self.command("new.sh", "check", extra={"ENV_DRY_RUN": "1"}, expected=1)
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.compose.parent.iterdir() if p.is_file()})
        self.assertEqual(self.main_snapshot(), self.before)

    def test_shared_pool_keeps_global_location_and_worktree_owner(self):
        self.manifest.write_text(self.manifest.read_text() + "\ndatabase_mode: shared\ndatabase_shared:\n"
                                 "  pool: vector\n  image: pgvector/pgvector:pg18\n  port: 35432\n")
        self.command("new.sh", "pooled", extra={"ENV_DRY_RUN": "1"})
        state = self.skill / "state/fixture/pooled/shared-database.json"
        data = json.loads(state.read_text())
        self.assertEqual(data["owner"]["root"], str(self.repo.resolve()))
        pool = self.skill / "state/_databases/fixture/vector/compose.json"
        service = json.loads(pool.read_text())["services"]["postgres"]
        self.assertEqual(service["image"], "pgvector/pgvector:pg18")
        self.assertIn("data:/var/lib/postgresql", service["volumes"])
        self.assertEqual(self.main_snapshot(), self.before)


if __name__ == "__main__":
    unittest.main()
