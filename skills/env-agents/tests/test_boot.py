"""Check observable dependency preparation, invalidation, and failure behavior."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

BOOT = Path(__file__).resolve().parents[1] / 'templates/boot.sh.tpl'

class BootTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='env-boot-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.bin = self.root / 'bin'
        self.bin.mkdir()
        for name, contents in {
            'node': 'echo node-test-runtime',
            'npm': '''echo install >> installs
[ "${FAIL_INSTALL:-0}" = 0 ] || exit 9
[ "${EMPTY_DEPENDENCIES:-0}" = 0 ] || exit 0
mkdir -p node_modules
echo '{}' > node_modules/.package-lock.json''',
            'php': '''case "$1" in
-v|-m) echo php-test-runtime ;;
artisan) echo migrate >> migrations; [ "${FAIL_MIGRATE:-0}" = 0 ] || exit 8 ;;
esac''',
            'composer': '''echo install >> installs
[ "${FAIL_INSTALL:-0}" = 0 ] || exit 9
mkdir -p vendor/composer
touch vendor/autoload.php
echo '{}' > vendor/composer/installed.json''',
        }.items():
            file = self.bin / name
            file.write_text('#!/bin/sh\nset -eu\n' + contents + '\n')
            file.chmod(0o755)
        self.env = {**os.environ, 'PATH': str(self.bin) + os.pathsep + os.environ['PATH']}
        (self.root / 'package.json').write_text('{}')
        (self.root / 'composer.json').write_text('{}')

    def boot(self, runtime='node', extra=None, expected=0):
        result = subprocess.run(['sh', str(BOOT), runtime, 'sh', '-c', 'echo ready >> served'], cwd=self.root, env={**self.env, **(extra or {})}, text=True, capture_output=True)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)

    def test_node_restart_skips_install_but_manifest_and_runtime_changes_invalidate(self):
        self.boot()
        self.boot()
        self.assertEqual((self.root / 'installs').read_text().splitlines(), ['install'])
        (self.root / 'package.json').write_text('{"version":"2"}')
        self.boot()
        (self.bin / 'node').write_text('#!/bin/sh\necho new-runtime\n')
        self.boot()
        self.assertEqual(len((self.root / 'installs').read_text().splitlines()), 3)

    def test_php_restart_checks_migrations_and_missing_autoload_reinstalls(self):
        self.boot('php')
        self.boot('php')
        self.assertEqual(len((self.root / 'installs').read_text().splitlines()), 1)
        self.assertEqual(len((self.root / 'migrations').read_text().splitlines()), 2)
        (self.root / 'vendor/autoload.php').unlink()
        self.boot('php')
        self.assertEqual(len((self.root / 'installs').read_text().splitlines()), 2)

    def test_node_project_without_dependencies_can_boot_and_resume(self):
        self.boot(extra={'EMPTY_DEPENDENCIES': '1'})
        self.boot(extra={'EMPTY_DEPENDENCIES': '1'})
        self.assertEqual(len((self.root / 'installs').read_text().splitlines()), 1)
        self.assertTrue((self.root / 'served').exists())

    def test_install_failure_does_not_serve_or_record_success(self):
        self.boot(extra={'FAIL_INSTALL': '1'}, expected=9)
        self.assertFalse((self.root / 'node_modules/.envstack-deps.sha256').exists())
        self.assertFalse((self.root / 'served').exists())
        self.boot()
        self.assertTrue((self.root / 'served').exists())

    def test_migration_failure_does_not_start_server(self):
        self.boot('php', extra={'FAIL_MIGRATE': '1'}, expected=8)
        self.assertFalse((self.root / 'served').exists())

if __name__ == '__main__':
    unittest.main()
