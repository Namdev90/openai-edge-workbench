import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import engine


NO_WHEEL = ('error: No solution found when resolving dependencies\n'
            'Because duckdb has no wheels with a matching Python ABI tag (cp315), '
            'your requirements are unsatisfiable.')


def catalog(*versions, cpu='x86_64'):
    return [{'key': f'cpython-{version}-windows-{cpu}-none', 'version': version} for version in versions]


def write_lock(path, packages):
    content = ''.join(name + '==1.0.0 \\\n    --hash=sha256:' + 'a' * 64 + '\n' for name in packages)
    Path(path).write_text(content, encoding='utf-8')
    return Path(path).read_bytes()


class PythonCompatibilityTests(unittest.TestCase):
    def test_stop_during_preflight_prevents_interpreter_installation(self):
        with tempfile.TemporaryDirectory() as temporary:
            workbench=self.workbench(temporary)
            def selected(*args):
                workbench.cancel.set()
                return catalog('3.14.8')[0]
            with patch.object(workbench,'find',return_value='uv.exe'), patch.object(workbench,'run_command',return_value=engine.CommandResult(0,'[]')) as command, patch.object(workbench,'preflight_python',side_effect=selected):
                with self.assertRaises(engine.StopRun):workbench.step_python()
            self.assertEqual(command.call_count,1)
            self.assertFalse((workbench.root/'environments').exists())

    def test_stop_after_interpreter_install_prevents_environment_creation(self):
        with tempfile.TemporaryDirectory() as temporary:
            workbench=self.workbench(temporary)
            def run(args,**kwargs):
                if args[1:3]==['python','install']:
                    workbench.cancel.set()
                    return engine.CommandResult(0,'installed')
                return engine.CommandResult(0,'[]')
            with patch.object(workbench,'find',return_value='uv.exe'), patch.object(workbench,'run_command',side_effect=run) as command, patch.object(workbench,'preflight_python',return_value=catalog('3.14.8')[0]):
                with self.assertRaises(engine.StopRun):workbench.step_python()
            self.assertEqual(command.call_count,2)
            self.assertFalse((workbench.root/'environments').exists())

    def workbench(self, path, **options):
        workbench = engine.Workbench(Path(path))
        workbench.current_result = {}
        workbench.arch = 'x64'
        workbench.options = {**engine.default_options(), **options}
        return workbench

    def test_selection_includes_newer_development_minor_and_skips_superseded_patches(self):
        data = catalog('3.16.0a1', '3.15.0rc2', '3.15.0', '3.14.7', '3.14.8', '3.10.20')
        data.extend(catalog('3.99.0', cpu='aarch64'))
        data.append({'key': 'cpython-3.99.0+freethreaded-windows-x86_64-none', 'version': '3.99.0'})
        self.assertEqual([x['version'] for x in engine.compatible_python_candidates(data, 'x64')],
                         ['3.16.0a1', '3.15.0', '3.14.8'])

    def test_optional_packs_are_included_before_interpreter_selection(self):
        self.assertEqual(engine.selected_python_packages({'toolkit': False, 'science': False}), ['openai', 'openai-agents'])
        self.assertIn('duckdb', engine.selected_python_packages({'toolkit': True, 'science': False}))
        self.assertIn('biopython', engine.selected_python_packages({'toolkit': False, 'science': True}))
        self.assertEqual(len(engine.selected_python_packages({'toolkit': True, 'science': True})), 20)

    def test_missing_wheels_selects_older_compatible_minor_before_any_install(self):
        with tempfile.TemporaryDirectory() as temporary:
            workbench = self.workbench(temporary)
            commands = []
            def run(args, **kwargs):
                commands.append(args)
                if args[args.index('--python-version') + 1] == '3.15.0':
                    return engine.CommandResult(1, NO_WHEEL)
                write_lock(args[args.index('--output-file') + 1], engine.selected_python_packages(workbench.options))
                return engine.CommandResult(0, 'Resolved 143 packages')
            with patch.object(workbench, 'run_command', side_effect=run):
                selected = workbench.preflight_python(catalog('3.15.0', '3.14.8'), 'x64', 'uv.exe')
            self.assertEqual(selected['version'], '3.14.8')
            self.assertTrue(all(command[1:3] == ['pip', 'compile'] for command in commands))
            evidence = workbench.report['python_compatibility']
            self.assertEqual([x['status'] for x in evidence['attempts']], ['INCOMPATIBLE', 'COMPATIBLE'])
            self.assertIn('duckdb', evidence['attempts'][0]['reason'])
            self.assertEqual(evidence['requirements_sha256'], hashlib.sha256(workbench.python_requirements_lock.read_bytes()).hexdigest())

    def test_newest_compatible_prerelease_is_used_without_trying_stable(self):
        with tempfile.TemporaryDirectory() as temporary:
            workbench = self.workbench(temporary, toolkit=False, science=False)
            def run(args, **kwargs):
                write_lock(args[args.index('--output-file') + 1], ['openai', 'openai-agents'])
                return engine.CommandResult(0, '')
            with patch.object(workbench, 'run_command', side_effect=run) as command:
                selected = workbench.preflight_python(catalog('3.16.0a1', '3.15.0'), 'x64', 'uv.exe')
            self.assertEqual(selected['version'], '3.16.0a1')
            self.assertEqual(command.call_count, 1)

    def test_transport_error_does_not_trigger_older_interpreter_selection(self):
        with tempfile.TemporaryDirectory() as temporary:
            workbench = self.workbench(temporary)
            result = engine.CommandResult(1, NO_WHEEL + '\nFailed to fetch https://pypi.org/simple/duckdb: certificate verify failed')
            with patch.object(workbench, 'run_command', return_value=result) as command:
                with self.assertRaises(engine.OperationError):
                    workbench.preflight_python(catalog('3.15.0', '3.14.8'), 'x64', 'uv.exe')
            self.assertEqual(command.call_count, 1)
            self.assertEqual(workbench.report['python_compatibility']['attempts'][0]['status'], 'PREFLIGHT_ERROR')
            self.assertIsNone(workbench.python_candidate)

    def test_unknown_resolver_failure_is_not_a_compatibility_proof(self):
        self.assertFalse(engine.python_resolution_incompatible(engine.CommandResult(1, 'unexpected internal error')))
        self.assertFalse(engine.python_resolution_incompatible(engine.CommandResult(2, NO_WHEEL)))
        self.assertFalse(engine.python_resolution_incompatible(engine.CommandResult(1, NO_WHEEL, True)))
        self.assertTrue(engine.python_resolution_incompatible(engine.CommandResult(1, NO_WHEEL)))

    def test_incomplete_lock_prevents_interpreter_selection(self):
        with tempfile.TemporaryDirectory() as temporary:
            workbench = self.workbench(temporary)
            def run(args, **kwargs):
                write_lock(args[args.index('--output-file') + 1], ['openai'])
                return engine.CommandResult(0, '')
            with patch.object(workbench, 'run_command', side_effect=run):
                with self.assertRaisesRegex(engine.OperationError, 'incomplete'):
                    workbench.preflight_python(catalog('3.15.0'), 'x64', 'uv.exe')
            self.assertFalse(hasattr(workbench, 'python_requirements_lock'))

    def prepare_candidate(self, workbench):
        python = workbench.root / 'candidate' / 'Scripts' / 'python.exe'
        python.parent.mkdir(parents=True)
        python.touch()
        lock = workbench.run_dir / 'requirements.txt'
        packages = engine.selected_python_packages(workbench.options)
        content = write_lock(lock, packages)
        workbench.python_requirements_lock = lock
        workbench.python_candidate = {'version': '3.14.8', 'command': [str(python)],
                                     'requirements_sha256': hashlib.sha256(content).hexdigest()}
        workbench.report['python_compatibility'] = {'resolved_versions': {name: '1.0.0' for name in packages}}

    def test_full_hashed_lock_installs_once_then_each_selected_pack_verifies_imports(self):
        with tempfile.TemporaryDirectory() as temporary:
            workbench = self.workbench(temporary)
            self.prepare_candidate(workbench)
            commands = []
            def run(args, **kwargs):
                commands.append(args)
                if args[1:3] == ['pip', 'install'] or args[1:3] == ['pip', 'check']:
                    return engine.CommandResult(0, 'All installed packages are compatible')
                code = args[2]
                selected = next(pack for pack in engine.PYTHON_PACKS.values() if repr(list(pack)) in code)
                return engine.CommandResult(0, json.dumps({name: '1.0.0' for name in selected}))
            with patch.object(workbench, 'find', return_value='uv.exe'), patch.object(workbench, 'run_command', side_effect=run):
                workbench.step_python_packages()
                workbench.step_documents()
                workbench.step_science()
            installs = [args for args in commands if args[1:3] == ['pip', 'install']]
            self.assertEqual(len(installs), 1)
            self.assertIn('--require-hashes', installs[0])
            self.assertIn(workbench.python_requirements_lock, installs[0])
            self.assertEqual(sum('importlib.import_module' in str(args) for args in commands), 3)
            self.assertFalse(workbench.python_candidate_failed)

    def test_changed_lock_is_rejected_before_any_install(self):
        with tempfile.TemporaryDirectory() as temporary:
            workbench = self.workbench(temporary)
            self.prepare_candidate(workbench)
            workbench.python_requirements_lock.write_text('duckdb==0.0.1', encoding='utf-8')
            with patch.object(workbench, 'find', return_value='uv.exe'), patch.object(workbench, 'run_command') as command:
                with self.assertRaisesRegex(engine.OperationError, 'changed'):
                    workbench.step_python_packages()
            command.assert_not_called()
            self.assertTrue(workbench.python_candidate_failed)

    def test_package_install_failure_preserves_previous_environment_without_retry(self):
        with tempfile.TemporaryDirectory() as temporary:
            workbench = self.workbench(temporary)
            self.prepare_candidate(workbench)
            previous = {'version': '3.13.9', 'command': ['previous-python.exe']}
            workbench.active['python'] = previous
            with patch.object(workbench, 'find', return_value='uv.exe'), patch.object(workbench, 'run_command', return_value=engine.CommandResult(1, 'download unavailable')) as command:
                with self.assertRaises(engine.OperationError): workbench.step_python_packages()
                workbench.activate_candidates()
            self.assertEqual(command.call_count, 1)
            self.assertTrue(workbench.python_candidate_failed)
            self.assertEqual(workbench.active['python'], previous)

    def test_optional_pack_import_failure_cannot_activate_candidate(self):
        with tempfile.TemporaryDirectory() as temporary:
            workbench = self.workbench(temporary)
            self.prepare_candidate(workbench)
            workbench.python_lock_installed = True
            previous = {'version': 'previous', 'command': ['previous.exe']}
            workbench.active['python'] = previous
            with patch.object(workbench, 'find', return_value='uv.exe'), patch.object(workbench, 'run_command', return_value=engine.CommandResult(1, 'ImportError: duckdb failed')):
                with self.assertRaises(engine.OperationError): workbench.step_documents()
                workbench.activate_candidates()
            self.assertEqual(workbench.active['python'], previous)


if __name__ == '__main__': unittest.main()
