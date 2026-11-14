"""Publicação e LaunchAgent com arquivos temporários e comandos simulados."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import plistlib
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import preview
import preview_launchagent as launchagent


class PreviewTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.project = self.root / 'projeto'; self.project.mkdir()
        self.source = self.project / 'proposta v1.html'; self.source.write_bytes(b'<html>versao um</html>')
        self.output = self.root / 'previews'
        self.environment = patch.dict(os.environ, {'BEZALEL_PREVIEWS_DIR': str(self.output)})
        self.environment.start(); self.addCleanup(self.environment.stop)
        self.host = patch.object(preview, 'tailnet_host', return_value='fixture.tailnet.ts.net')
        self.host.start(); self.addCleanup(self.host.stop)

    def test_empty_previews_override_uses_home_default(self):
        with patch.dict(os.environ, BEZALEL_PREVIEWS_DIR=''), patch.object(Path, 'home', return_value=self.root):
            self.assertEqual(preview.previews_dir(), self.root/'previews')

    def test_copy_preserves_original_and_url_encodes_filename(self):
        result = preview.publish(self.project, 21, self.source)
        destination = self.output / 'projeto/issue-21/proposta v1.html'
        self.assertEqual(destination.read_bytes(), self.source.read_bytes())
        self.assertTrue(self.source.exists())
        self.assertEqual(result['url'], 'https://fixture.tailnet.ts.net/projeto/issue-21/proposta%20v1.html')
        self.assertTrue(result['created'])
        self.source.unlink()  # Exclusão do original da tarefa preserva a cópia.
        self.assertTrue(destination.exists())

    def test_same_bytes_are_idempotent_and_another_version_is_preserved(self):
        first = preview.publish(self.project, 21, self.source)
        self.assertFalse(preview.publish(self.project, 21, self.source)['created'])
        self.source.write_bytes(b'<html>versao dois</html>')
        with self.assertRaisesRegex(preview.PreviewError, 'outro nome'):
            preview.publish(self.project, 21, self.source)
        self.assertEqual(Path(first['file']).read_bytes(), b'<html>versao um</html>')
        self.assertEqual(list(Path(first['file']).parent.glob('.preview-*')), [])
        second_source = self.source.with_name('proposta-v2.html'); second_source.write_bytes(self.source.read_bytes())
        second = preview.publish(self.project, 21, second_source)
        self.assertNotEqual(first['file'], second['file'])

    def test_concurrent_publish_never_replaces_the_winner(self):
        def publish(_):
            return preview.publish(self.project, 21, self.source)
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(publish, range(16)))
        self.assertEqual(sum(result['created'] for result in results), 1)
        self.assertEqual(Path(results[0]['file']).read_bytes(), self.source.read_bytes())
        self.assertEqual(list(Path(results[0]['file']).parent.glob('.preview-*')), [])

    def test_project_config_controls_directory_and_rejects_traversal(self):
        (self.project / '.bezalel').mkdir()
        config = self.project / '.bezalel/project.json'
        config.write_text(json.dumps({'project': 'nome-real'}))
        self.assertIn('/nome-real/issue-21/', preview.publish(self.project, 21, self.source)['file'])
        for value in ['../outro', '/etc', '', None, 'PROJETO']:
            config.write_text(json.dumps({'project': value}))
            with self.assertRaises(preview.PreviewError):
                preview.publish(self.project, 21, self.source)

    def test_symlink_destination_or_source_is_not_followed(self):
        other = self.root / 'other'; other.mkdir()
        self.output.symlink_to(other, target_is_directory=True)
        with self.assertRaises(preview.PreviewError):
            preview.publish(self.project, 21, self.source)
        self.assertEqual(list(other.iterdir()), [])
        self.output.unlink()
        linked = self.project / 'link.html'; linked.symlink_to(self.source)
        with self.assertRaises(preview.PreviewError):
            preview.publish(self.project, 21, linked)

    def test_conflicting_destination_symlink_is_not_replaced(self):
        directory = self.output / 'projeto/issue-21'; directory.mkdir(parents=True)
        destination = directory / self.source.name; destination.symlink_to(self.source)
        with self.assertRaises(preview.PreviewError):
            preview.publish(self.project, 21, self.source)
        self.assertTrue(destination.is_symlink())

    def test_bad_issue_and_missing_source_have_no_publication(self):
        for issue in [0, -1]:
            with self.assertRaises(preview.PreviewError):
                preview.publish(self.project, issue, self.source)
        with self.assertRaises(preview.PreviewError):
            preview.publish(self.project, 21, self.project / 'missing.html')
        self.assertFalse(self.output.exists())


class HostTests(unittest.TestCase):
    def test_hostname_uses_only_status_read_and_configured_binary(self):
        result = subprocess.CompletedProcess([], 0, json.dumps({'Self': {'DNSName': 'fixture.tail.ts.net.'}}), '')
        with patch.dict(os.environ, ENV_TAILSCALE_BIN='/fixture/tailscale'), patch.object(preview.subprocess, 'run', return_value=result) as command:
            self.assertEqual(preview.tailnet_host(), 'fixture.tail.ts.net')
            self.assertEqual(command.call_args.args[0], ['/fixture/tailscale', 'status', '--json'])

    def test_unavailable_or_invalid_hostname_is_error(self):
        for result in [subprocess.CompletedProcess([], 1, '', ''),
                       subprocess.CompletedProcess([], 0, '{}', ''),
                       subprocess.CompletedProcess([], 0, '{"Self":{"DNSName":"x/other"}}', '')]:
            with patch.dict(os.environ, ENV_TAILSCALE_BIN='/fixture/tailscale'), patch.object(preview.subprocess, 'run', return_value=result):
                with self.assertRaises(preview.PreviewError): preview.tailnet_host()


class LaunchAgentTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(); self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.calls = []; self.loaded = False
        patches = [patch.dict(os.environ, {'BEZALEL_PREVIEWS_DIR': str(self.root / 'previews'), 'XDG_STATE_HOME': str(self.root / 'state')}),
                   patch.object(Path, 'home', return_value=self.root),
                   patch.object(launchagent.sys, 'platform', 'darwin'),
                   patch.object(launchagent, 'port_in_use', return_value=False),
                   patch.object(launchagent.subprocess, 'run', side_effect=self.command)]
        for item in patches:
            item.start(); self.addCleanup(item.stop)

    def command(self, args, **kwargs):
        self.calls.append(args)
        code = 0
        if args[1] == 'print': code = 0 if self.loaded else 113
        elif args[1] == 'bootstrap': self.loaded = True
        else: self.fail('Comando mutável inesperado: ' + repr(args))
        return subprocess.CompletedProcess(args, code, b'', b'')

    def test_plan_does_not_write_or_execute_and_binds_only_loopback(self):
        result = launchagent.plan()
        self.assertFalse(result['installed'])
        self.assertEqual(result['listen'], '127.0.0.1:8000')
        self.assertEqual(result['arguments'][1:7], ['-B', '-m', 'http.server', '8000', '--bind', '127.0.0.1'])
        self.assertEqual(self.calls, [])
        self.assertEqual(list(self.root.iterdir()), [])

    def test_install_is_idempotent_with_only_bootstrap_and_read(self):
        result = launchagent.install()
        self.assertTrue(result['installed']); self.assertTrue(result['changed'])
        path = Path(result['file']); original = path.read_bytes()
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        second = launchagent.install()
        self.assertFalse(second['changed'])
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(sum(args[1] == 'bootstrap' for args in self.calls), 1)
        self.assertTrue(all(args[1] in ('print', 'bootstrap') for args in self.calls))

    def test_existing_listener_is_preserved_without_writes(self):
        with patch.object(launchagent, 'port_in_use', return_value=True):
            with self.assertRaisesRegex(preview.PreviewError, 'ocupada'): launchagent.install()
        self.assertFalse(Path(launchagent.plan()['file']).exists())
        self.assertFalse(any(args[1] == 'bootstrap' for args in self.calls))

    def test_customized_plist_is_preserved(self):
        path = Path(launchagent.plan()['file']); path.parent.mkdir(parents=True)
        path.write_text('customized')
        with self.assertRaisesRegex(preview.PreviewError, 'diverge'): launchagent.install()
        self.assertEqual(path.read_text(), 'customized')
        self.assertEqual(self.calls, [])

    def test_paths_are_xml_escaped(self):
        with patch.dict(os.environ, BEZALEL_PREVIEWS_DIR=str(self.root / 'a&b')):
            content, _ = launchagent.configuration()
            self.assertIn(str(self.root / 'a&b'), plistlib.loads(content)['ProgramArguments'])
            self.assertIn(b'a&amp;b', content)

    def test_bootstrap_failure_is_not_success_and_plist_remains(self):
        def fail_bootstrap(args, **kwargs):
            return subprocess.CompletedProcess(args, 113, b'', b'')
        with patch.object(launchagent.subprocess, 'run', side_effect=fail_bootstrap):
            with self.assertRaisesRegex(preview.PreviewError, 'Falha'): launchagent.install()
        self.assertTrue(Path(launchagent.plan()['file']).is_file())


if __name__ == '__main__':
    unittest.main()
