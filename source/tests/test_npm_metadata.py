import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import engine


class NpmMetadataTests(unittest.TestCase):
    version = 'v27.0.0-nightly202610086d5e309871'
    warning = ('npm warn cli npm v12.1.0 does not support Node.js '
               'v27.0.0-nightly202610086d5e309871. This version of npm supports '
               'the following node versions: `^22.22.2 || ^24.15.0 || >=26.0.0`.')

    def exercise_node(self, root, output):
        w = engine.Workbench(Path(root))
        w.current_result = {'status': 'RUNNING'}
        w.arch = 'x64'
        directory = w.root / 'runtimes' / 'node' / (self.version + '-x64')
        exe = directory / ('node-' + self.version + '-win-x64') / 'node.exe'
        npm = exe.parent / 'node_modules/npm/bin/npm-cli.js'
        npm.parent.mkdir(parents=True)
        exe.touch()
        npm.touch()
        (directory / '.workbench-owned.json').write_text('{}')
        catalog = [{'version': self.version, 'files': ['win-x64-zip']}]
        responses = [engine.CommandResult(0, self.version), engine.CommandResult(0, output)]
        with patch.object(w, 'get_json', return_value=catalog), patch.object(w, 'run_command', side_effect=responses):
            w.step_node()
        return w

    def test_warning_is_preserved_separately_from_version(self):
        with tempfile.TemporaryDirectory() as root:
            w = self.exercise_node(root, self.warning + '\n12.1.0')
            self.assertEqual(w.active['npm']['version'], '12.1.0')
            self.assertEqual(w.active['npm']['diagnostics'], [self.warning])
            self.assertEqual(w.current_result['status'], 'REVIEW_NEEDED')
            saved = json.loads(w.state_file.read_text())
            self.assertEqual(saved['tools']['npm']['version'], '12.1.0')
            self.assertIn(self.warning, saved['tools']['npm']['diagnostics'])

    def test_plain_prerelease_version_does_not_create_warning(self):
        with tempfile.TemporaryDirectory() as root:
            w = self.exercise_node(root, '\n\x1b[0m\n12.2.0-beta.1\n')
            self.assertEqual(w.active['npm']['version'], '12.2.0-beta.1')
            self.assertEqual(w.active['npm']['diagnostics'], [])
            self.assertEqual(w.current_result['status'], 'RUNNING')

    def test_warning_without_actual_version_fails(self):
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaisesRegex(engine.OperationError, 'unambiguous version'):
                self.exercise_node(root, self.warning)

    def test_multiple_version_lines_fail(self):
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaisesRegex(engine.OperationError, 'unambiguous version'):
                self.exercise_node(root, '12.1.0\n12.2.0')


if __name__ == '__main__':
    unittest.main()
