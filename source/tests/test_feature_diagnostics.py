"""Boundary and failure tests for the explicit manual diagnostic catalog."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from engine import SCHEMA, assert_regular_path
import feature_diagnostics as diagnostics


class Context:
    def __init__(self, root):
        self.root = root
        self.workbench = SimpleNamespace(active={})
        self.simulate = False
        self.commands = []
        self.response = {'exit_code': 0, 'output': ''}
        self.catalogs = {}
        self.report = {}
        self.snap = {'started': False, 'finished': False, 'cancel_requested': False}

    def command(self, argv, timeout=20):
        self.commands.append((argv, timeout))
        if isinstance(self.response, Exception):
            raise self.response
        return self.response

    def fetch_json(self, url):
        if url not in self.catalogs:
            raise OSError('Publisher network unavailable.')
        return self.catalogs[url]

    def safe_path(self, path):
        assert_regular_path(path)

    def snapshot(self):
        return self.snap

    def latest_report(self):
        return self.report

    def history(self):
        return []

    def tool(self, name, filenames, version='1.0.0'):
        paths = []
        for filename in filenames:
            p = self.root / 'runtimes' / name / version / filename
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(b'fixture entry point')
            paths.append(str(p))
        self.workbench.active[name] = {'version': version, 'command': paths}
        return paths


class DiagnosticFeaturesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.ctx = Context(self.root)

    def run_feature(self, feature_id):
        return diagnostics.run(feature_id, self.ctx, {})

    def test_catalog_has_exact_thirty_stable_distinct_ids(self):
        self.assertEqual([x['id'] for x in diagnostics.FEATURES], [f'f{i:03}' for i in range(1, 31)])
        self.assertEqual(len({x['title'] for x in diagnostics.FEATURES}), 30)
        self.assertTrue(all(x['category'] == 'Diagnostics' and x['effect'] == 'read-only' for x in diagnostics.FEATURES))

    def test_unknown_ids_and_browser_options_are_rejected(self):
        for feature_id, payload in [('f000', {}), ('f031', {}), ('f001', {'command': 'whoami'}), ('f001', ['path'])]:
            with self.subTest(feature_id=feature_id, payload=payload):
                with self.assertRaises(ValueError):
                    diagnostics.run(feature_id, self.ctx, payload)

    def test_result_scrubs_secret_email_and_url_queries(self):
        secret = 'ghp_123456789abcdefghijklmnopqrstuvwxyz'
        self.ctx.tool('npm', ['node.exe', 'npm-cli.js'])
        self.ctx.response = {'exit_code': 1, 'output': f'Bearer {secret}\nuser@example.com\nhttps://registry.npmjs.org/?token={secret}'}
        result = self.run_feature('f017')
        serialized = json.dumps(result)
        self.assertNotIn(secret, serialized)
        self.assertNotIn('user@example.com', serialized)
        self.assertIn('[REDACTED]', serialized)
        self.assertFalse(result['data']['clean_version_output'])

    def test_outside_root_command_is_not_executed(self):
        self.ctx.workbench.active['npm'] = {'version': '1.0.0', 'command': [str(self.root.parent / 'node.exe'), str(self.root / 'runtimes/npm/npm-cli.js')]}
        result = self.run_feature('f017')
        self.assertFalse(result['data']['available'])
        self.assertEqual(self.ctx.commands, [])

    def test_dotdot_escape_and_relative_paths_are_rejected(self):
        for path in [self.root / '..' / 'node.exe', Path('runtimes/node.exe')]:
            with self.subTest(path=path):
                with self.assertRaises(ValueError):
                    diagnostics._managed(self.ctx, path)

    def test_unlisted_entry_point_inside_root_is_not_executed(self):
        self.ctx.tool('node', ['unexpected.cmd'])
        result = self.run_feature('f018')
        self.assertFalse(result['data']['available'])
        self.assertEqual(self.ctx.commands, [])

    def test_workspace_entry_point_is_not_executed(self):
        p = self.root / 'workspace' / 'node.exe'; p.parent.mkdir(); p.write_bytes(b'x')
        self.ctx.workbench.active['node'] = {'version': '1.0.0', 'command': [str(p)]}
        self.assertFalse(self.run_feature('f018')['data']['available'])
        self.assertEqual(self.ctx.commands, [])

    def test_symlinked_managed_directory_is_refused(self):
        target = self.root / 'target'; target.mkdir()
        link = self.root / 'runtimes'
        try:
            link.symlink_to(target, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest('Host cannot create a directory symlink.')
        with self.assertRaises(ValueError):
            diagnostics._managed(self.ctx, link / 'node.exe')

    def test_npm_clean_exact_version_is_confirmed(self):
        paths = self.ctx.tool('npm', ['node.exe', 'npm-cli.js'], version='12.2.0')
        self.ctx.response = {'exit_code': 0, 'output': '12.2.0\n'}
        result = self.run_feature('f017')
        self.assertTrue(result['data']['clean_version_output'])
        self.assertNotIn('warnings', result)
        self.assertEqual(self.ctx.commands, [(paths + ['--version'], 20)])

    def test_npm_warning_and_version_mismatch_are_not_suppressed(self):
        self.ctx.tool('npm', ['node.exe', 'npm-cli.js'], version='12.2.0')
        for output in ['npm warn cli incompatible node\n12.2.0\n', '12.1.0\n', '12.2.0\n12.2.0\n']:
            with self.subTest(output=output):
                self.ctx.response = {'exit_code': 0, 'output': output}
                result = self.run_feature('f017')
                self.assertFalse(result['data']['clean_version_output'])
                self.assertTrue(result['warnings'])

    def test_command_failure_and_timeout_are_explicit(self):
        self.ctx.tool('npm', ['node.exe', 'npm-cli.js'])
        for response in [{'exit_code': 3, 'output': 'failed'}, TimeoutError('Timed out'), {'output': 'no exit code'}]:
            self.ctx.response = response
            result = self.run_feature('f017')
            self.assertFalse(result['data']['ok'])
            self.assertFalse(result['data']['clean_version_output'])
            self.assertTrue(result['warnings'])

    def test_missing_binary_report_is_read_only(self):
        paths = self.ctx.tool('node', ['node.exe'])
        Path(paths[0]).unlink()
        result = self.run_feature('f010')
        self.assertFalse(result['data'][0]['available'])
        self.assertEqual(self.ctx.commands, [])
        self.assertFalse(Path(paths[0]).exists())

    def test_ownership_records_are_validated_without_cleanup(self):
        valid = self.root / 'runtimes/node/valid'; valid.mkdir(parents=True)
        invalid = self.root / 'environments/python-invalid'; invalid.mkdir(parents=True)
        (valid / '.workbench-owned.json').write_text(json.dumps({'owned_by': SCHEMA, 'version': 'v27.0.0-nightly'}))
        (invalid / '.workbench-owned.json').write_text(json.dumps({'owned_by': 'some-other-project', 'version': '1.0.0'}))
        result = self.run_feature('f013')
        self.assertEqual(sum(x['valid'] for x in result['data']['markers']), 1)
        self.assertTrue(result['warnings'])
        self.assertTrue(invalid.exists())

    def test_malformed_and_missing_markers_are_preserved(self):
        for directory, content in [('bad-json', '{'), ('bad-shape', '[]'), ('missing', None)]:
            path = self.root / 'environments' / directory; path.mkdir(parents=True)
            if content:
                (path / '.workbench-owned.json').write_text(content)
        result = self.run_feature('f013')
        self.assertEqual(len(result['data']['markers']), 3)
        self.assertTrue(all(not x['valid'] for x in result['data']['markers']))
        self.assertTrue(all((self.root / 'environments' / n).exists() for n in ('bad-json', 'bad-shape', 'missing')))

    def test_escaped_oserror_filename_is_not_exported(self):
        secret_path = r'C:\Users\private-account\AppData\Local\private-file.json'
        error = FileNotFoundError(2, 'Required file is missing', secret_path)
        self.ctx.tool('npm', ['node.exe', 'npm-cli.js'])
        self.ctx.response = error
        result = self.run_feature('f017')
        self.assertNotIn('private-account', json.dumps(result))
        self.assertNotIn('private-file', json.dumps(result))
        self.assertIn('Required file is missing', result['data']['output'])

    def test_generation_inventory_marks_active_entry_points(self):
        self.ctx.tool('node', ['node.exe'])
        (self.root / 'runtimes/node/old').mkdir()
        result = self.run_feature('f011')
        self.assertEqual(sum(x['active'] for x in result['data']['generations']), 1)
        self.assertEqual(len(result['data']['generations']), 2)

    def test_storage_scan_uses_metadata_and_excludes_private_backups(self):
        managed = self.root / 'downloads/archive.zip'; managed.parent.mkdir(); managed.write_bytes(b'12345')
        private = self.root / 'private-backups/config.toml'; private.parent.mkdir(); private.write_text('credential must not appear')
        result = self.run_feature('f012')
        self.assertEqual(result['data']['groups']['downloads'], {'bytes': 5, 'files': 1})
        self.assertNotIn('credential', json.dumps(result))
        self.assertEqual(self.ctx.commands, [])

    def test_storage_scan_returns_partial_when_time_budget_is_reached(self):
        p = self.root / 'downloads/file.bin'; p.parent.mkdir(); p.write_bytes(b'123')
        with patch.object(diagnostics.time, 'monotonic', side_effect=[0, 16]):
            result = self.run_feature('f012')
        self.assertTrue(result['data']['partial'])
        self.assertEqual(result['data']['scanned_files'], 1)
        self.assertTrue(result['warnings'])

    def test_reparse_generations_are_listed_without_following_them(self):
        alias = self.root / 'runtimes/node/alias'; alias.mkdir(parents=True)
        regular = self.root / 'runtimes/node/regular'; regular.mkdir()
        (alias / '.workbench-owned.json').write_text('do not inspect this target')
        (regular / '.workbench-owned.json').write_text(json.dumps({'owned_by': SCHEMA, 'version': '1.0.0'}))
        for feature_id in ('f011', 'f013'):
            with self.subTest(feature_id=feature_id), patch.object(diagnostics, 'is_reparse', side_effect=lambda p: Path(p) == alias), patch.object(self.ctx, 'safe_path', wraps=self.ctx.safe_path) as boundary:
                result = self.run_feature(feature_id)
            self.assertEqual(result['data']['excluded_reparse_paths'], [str(alias.relative_to(self.root))])
            self.assertNotIn(alias, [call.args[0] for call in boundary.call_args_list])
            self.assertNotIn('do not inspect', json.dumps(result))
            self.assertTrue(result['warnings'])

    def test_fingerprints_match_actual_bytes_but_do_not_claim_authenticity(self):
        paths = self.ctx.tool('node', ['node.exe'])
        result = self.run_feature('f014')
        self.assertEqual(result['data']['files'][0]['sha256'], hashlib.sha256(Path(paths[0]).read_bytes()).hexdigest())
        self.assertIn('does not prove', result['data']['publisher_comparison'])

    def test_provenance_projects_only_approved_fields(self):
        status = {'repository': 'Namdev90/openai-edge-workbench', 'commit': 'a' * 40, 'state': 'VERIFIED_GITHUB_COMMIT', 'utc': '2026-10-10', 'token': 'do not export', 'error': 'private details'}
        (self.root / 'Setup-Status.json').write_text(json.dumps(status))
        result = self.run_feature('f015')
        self.assertTrue(result['data']['valid_commit_identity'])
        self.assertNotIn('token', result['data'])
        self.assertNotIn('error', result['data'])
        self.assertNotIn('warnings', result)

    def test_cached_or_malformed_provenance_is_an_observation(self):
        (self.root / 'Setup-Status.json').write_text(json.dumps({'commit': 'bad', 'state': 'UPDATE_FAILED_VERIFIED_CACHE'}))
        result = self.run_feature('f015')
        self.assertFalse(result['data']['valid_commit_identity'])
        self.assertTrue(result['warnings'])

    def test_python_isolation_does_not_export_prefixes_or_read_user_hooks(self):
        paths = self.ctx.tool('python', ['python.exe'])
        self.ctx.response = {'exit_code': 0, 'output': json.dumps({'prefix_is_managed': True, 'virtual_environment': True, 'user_site_enabled': False, 'isolated': True})}
        result = self.run_feature('f019')
        self.assertTrue(result['data']['environment_isolated'])
        self.assertEqual(self.ctx.commands[0][0][:4], paths + ['-I', '-B', '-c'])
        self.assertNotIn(str(self.root), json.dumps(result))
        self.assertNotIn('prefix', result['data'])

    def test_malformed_python_evidence_is_never_success(self):
        self.ctx.tool('python', ['python.exe'])
        for output in ['not json', '{}', json.dumps({'prefix_is_managed': 'yes', 'virtual_environment': True, 'user_site_enabled': False, 'isolated': True})]:
            self.ctx.response = {'exit_code': 0, 'output': output}
            self.assertFalse(self.run_feature('f019')['data']['available'])

    def test_node_catalog_filters_architecture_and_real_nightly_entries(self):
        self.ctx.workbench.active['node'] = {'version': 'v27.0.0-nightly20261008abc'}
        self.ctx.catalogs['https://nodejs.org/download/nightly/index.json'] = [
            {'version': 'v27.0.0-nightly20261008abc', 'files': ['win-x64-zip']},
            {'version': 'v28.0.0-nightly20261009def', 'files': ['win-arm64-zip']},
            {'version': 'v29.0.0', 'files': ['win-x64-zip']},
            {'version': 'malformed', 'files': ['win-x64-zip']},
        ]
        with patch.object(diagnostics, 'architecture', return_value='x64'):
            result = self.run_feature('f023')
        self.assertTrue(result['data']['current'])
        self.assertEqual(result['data']['architecture'], 'x64')

    def test_node_catalog_uses_native_architecture_under_emulation(self):
        self.ctx.workbench.active['node'] = {'version': 'v28.0.0-nightly20261009def'}
        self.ctx.catalogs['https://nodejs.org/download/nightly/index.json'] = [
            {'version': 'v27.0.0-nightly20261008abc', 'files': ['win-x64-zip']},
            {'version': 'v28.0.0-nightly20261009def', 'files': ['win-arm64-zip']},
        ]
        with patch.dict(os.environ, {'PROCESSOR_ARCHITEW6432': 'ARM64', 'PROCESSOR_ARCHITECTURE': 'AMD64'}):
            result = self.run_feature('f023')
        self.assertEqual(result['data']['architecture'], 'arm64')
        self.assertTrue(result['data']['current'])

    def test_scrub_handles_secret_mapping_keys_and_sensitive_labels(self):
        result = diagnostics._result('A record.', {'github_pat_secretkey': {'ACCESS_TOKEN': 'opaque-secret', 'innocent': 'value'}})
        text = json.dumps(result)
        self.assertNotIn('github_pat_secretkey', text)
        self.assertNotIn('opaque-secret', text)
        self.assertIn('value', text)

    def test_official_network_failure_is_not_current(self):
        result = self.run_feature('f023')
        self.assertFalse(result['data']['available'])
        self.assertTrue(result['warnings'])

    def test_npm_catalog_does_not_select_deprecated_or_platform_wrappers(self):
        self.ctx.workbench.active['npm'] = {'version': '12.2.0'}
        self.ctx.catalogs['https://registry.npmjs.org/npm'] = {'versions': {
            '12.2.0': {'engines': {'node': '>=26.0.0'}},
            '99.0.0': {'deprecated': 'removed'},
            '15.0.0-linux': {},
        }}
        result = self.run_feature('f024')
        self.assertTrue(result['data']['current'])
        self.assertEqual(result['data']['newest_supported_package'], '12.2.0')

    def test_dotnet_catalog_accepts_go_live_rc_without_guessing_daily_identity(self):
        self.ctx.catalogs['https://builds.dotnet.microsoft.com/dotnet/release-metadata/releases-index.json'] = {'releases-index': [{'channel-version': '11.0', 'latest-sdk': '11.0.100-rc.1', 'support-phase': 'go-live'}]}
        result = self.run_feature('f025')
        self.assertEqual(result['data']['channel'], '11.0')
        self.assertIn('does not establish', result['data']['scope'])

    def test_malformed_catalogs_are_explicitly_unavailable(self):
        for feature_id, url, value in [('f023', 'https://nodejs.org/download/nightly/index.json', {}), ('f024', 'https://registry.npmjs.org/npm', []), ('f025', 'https://builds.dotnet.microsoft.com/dotnet/release-metadata/releases-index.json', {'releases-index': []})]:
            self.ctx.catalogs[url] = value
            result = self.run_feature(feature_id)
            self.assertFalse(result['data']['available'])
            self.assertTrue(result['warnings'])

    def test_tls_failures_report_fixed_hosts_and_no_success(self):
        with patch.object(socket, 'create_connection', side_effect=OSError('Certificate or transport unavailable')) as connect:
            result = self.run_feature('f027')
        self.assertEqual(connect.call_count, 3)
        self.assertTrue(all(not x['certificate_verified'] for x in result['data']))
        self.assertEqual({call.args[0][0] for call in connect.call_args_list}, {'nodejs.org', 'registry.npmjs.org', 'builds.dotnet.microsoft.com'})
        self.assertTrue(result['warnings'])

    def test_variable_presence_never_exposes_values(self):
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'secretfixturevalue', 'HTTP_PROXY': 'http://secret-proxy.example', 'USERPROFILE': str(self.root), 'HOME': str(self.root)}, clear=True):
            result = self.run_feature('f028')
        self.assertTrue(result['data']['OPENAI_API_KEY'])
        self.assertFalse(result['data']['GITHUB_TOKEN'])
        self.assertNotIn('secretfixturevalue', json.dumps(result))
        self.assertNotIn('secret-proxy', json.dumps(result))

    def test_migration_review_reports_counts_not_settings_or_contents(self):
        self.ctx.report = {'migrations': {'editor_files': {'copied': ['private-settings-name'], 'conflicts': ['secret-config-name'], 'skipped': []}, 'editor_extensions': {'failed': ['ext.private']}}}
        result = self.run_feature('f029')
        self.assertEqual(result['data']['conflicts'], 1)
        self.assertEqual(result['data']['extension_failures'], 1)
        self.assertNotIn('secret-config-name', json.dumps(result))
        self.assertNotIn('private-settings-name', json.dumps(result))
        self.assertTrue(result['warnings'])

    def test_missing_migration_record_is_not_silently_verified(self):
        result = self.run_feature('f029')
        self.assertFalse(result['data']['migration_record_present'])
        self.assertTrue(result['warnings'])

    def test_session_hygiene_does_not_read_session_capability(self):
        (self.root / 'local-session.json').write_text('This is deliberately not JSON; never read the capability.')
        (self.root / 'workbench.lock').write_text('')
        self.ctx.snap = {'started': True, 'finished': False, 'cancel_requested': True}
        result = self.run_feature('f030')
        self.assertTrue(result['data']['session_file_present'])
        self.assertTrue(result['data']['lock_file_present'])
        self.assertFalse(result['data']['stale_lock_assumed'])
        self.assertNotIn('capability.', json.dumps(result))
        self.assertTrue(result['warnings'])

    def test_path_diagnostics_do_not_rewrite_the_environment(self):
        existing = self.root / 'existing'; existing.mkdir()
        original = os.pathsep.join([str(existing), str(self.root / 'missing'), str(existing)])
        with patch.dict(os.environ, {'PATH': original}):
            missing = self.run_feature('f006')
            duplicate = self.run_feature('f007')
            self.assertEqual(os.environ['PATH'], original)
        self.assertEqual(len(missing['data']['missing']), 1)
        self.assertEqual(duplicate['data']['duplicates'][0]['positions'], [0, 2])
        self.assertNotIn(str(existing), json.dumps(missing))
        self.assertNotIn(str(existing), json.dumps(duplicate))

    def test_cli_collision_reports_positions_without_path_values(self):
        folders = [self.root / 'first-private-folder', self.root / 'second-private-folder']
        for folder in folders:
            folder.mkdir(); (folder / 'node.exe').write_bytes(b'x')
        # Emulate Windows suffixes and PATH separators only inside this module;
        # changing the shared os.name makes pathlib select WindowsPath on Linux.
        native_os_name = os.name
        windows_os = SimpleNamespace(name='nt', path=os.path, pathsep=';',
                                     environ={'PATH': ';'.join(map(str, folders))})
        with patch.object(diagnostics, 'os', windows_os):
            self.assertEqual(os.name, native_os_name)
            self.assertIsInstance(Path('.'), type(self.root))
            result = self.run_feature('f008')
        self.assertEqual(result['data']['collisions']['node'], [{'path_position': 0, 'entry_name': 'node.exe'}, {'path_position': 1, 'entry_name': 'node.exe'}])
        self.assertNotIn('private-folder', json.dumps(result))

    def test_completed_report_selection_is_allowed_but_paths_are_not(self):
        self.ctx.report = {'migrations': {'editor_files': {'conflicts': [], 'copied': [], 'skipped': []}}}
        result = diagnostics.run('f029', self.ctx, {'run_id': '20261010-173209-ae4444'})
        self.assertTrue(result['data']['migration_record_present'])
        for payload in [{'run_id': '../private-backups'}, {'run_id': 123}, {'options': {}}, {'run_id': '20261010-173209-ae4444', 'path': str(self.root)}]:
            with self.assertRaises(ValueError):
                diagnostics.run('f029', self.ctx, payload)

    def test_simulation_executes_no_query_or_tls_probe(self):
        self.ctx.simulate = True
        with patch.object(socket, 'create_connection') as network, patch.object(diagnostics, '_powershell') as powershell:
            for feature_id in ('f002', 'f017', 'f023', 'f027', 'f029'):
                result = self.run_feature(feature_id)
                self.assertFalse(result['data']['executed'])
                self.assertIn('SIMULATED', result['summary'])
        network.assert_not_called(); powershell.assert_not_called()
        self.assertEqual(self.ctx.commands, [])

    def test_context_null_exit_code_retains_actual_timeout_evidence(self):
        self.ctx.tool('npm', ['node.exe', 'npm-cli.js'])
        self.ctx.response = {'exit_code': None, 'output': 'Diagnostic timed out; no success inferred.'}
        result = self.run_feature('f017')
        self.assertFalse(result['data']['ok'])
        self.assertIn('timed out', result['data']['output'])

    def test_curated_alias_failure_preserves_other_manager_evidence(self):
        with patch.object(diagnostics.shutil, 'which', return_value=str(self.root / 'alias')), patch.object(self.ctx, 'safe_path', side_effect=ValueError('Refused alias')), patch.object(diagnostics, '_powershell', side_effect=ValueError('Registered package unavailable')):
            result = self.run_feature('f021')
        self.assertEqual(set(result['data']), {'winget', 'uv', 'git', 'gh'})
        self.assertTrue(all(not row['ok'] for row in result['data'].values()))
        self.assertTrue(result['warnings'])

    def test_registered_winget_fallback_requires_signature_and_fixed_package(self):
        evidence = {'available': True, 'exit_code': 0, 'output': 'v1.15.1', 'ok': True}
        with patch.object(diagnostics.os, 'name', 'nt'), patch.object(diagnostics.shutil, 'which', return_value=str(self.root / 'alias')), patch.object(self.ctx, 'safe_path', side_effect=ValueError('Refused alias')), patch.object(diagnostics, '_powershell', return_value=evidence) as query:
            result = diagnostics._curated(self.ctx, 'winget', ['--version'])
        self.assertTrue(result['ok'])
        self.assertIn('Microsoft.DesktopAppInstaller', query.call_args.args[1])
        self.assertIn('Get-AuthenticodeSignature', query.call_args.args[1])
        self.assertIn("-ne 'Valid'", query.call_args.args[1])
        self.assertEqual(self.ctx.commands, [])

    def test_zero_available_memory_is_real_pressure_not_unavailable(self):
        with patch.object(diagnostics, '_powershell', return_value={'total_kib': 8 * 1024**2, 'free_kib': 0}):
            result = self.run_feature('f002')
        self.assertEqual(result['data']['free_kib'], 0)
        self.assertTrue(result['warnings'])

    def test_memory_provider_inconsistent_or_malformed_data_is_rejected(self):
        for observation in [{'total_kib': 1, 'free_kib': 2}, {'total_kib': 100, 'free_kib': '50'}, {}, {'total_kib': 0, 'free_kib': 0}]:
            with self.subTest(observation=observation):
                with patch.object(diagnostics, '_powershell', return_value=observation):
                    self.assertFalse(self.run_feature('f002')['data']['available'])

    def test_processor_topology_has_validated_numeric_totals(self):
        with patch.object(diagnostics, '_powershell', return_value=[{'NumberOfCores': 4, 'NumberOfLogicalProcessors': 8, 'AddressWidth': 64}, {'NumberOfCores': 2, 'NumberOfLogicalProcessors': 4, 'AddressWidth': 64}]):
            result = self.run_feature('f004')
        self.assertEqual(result['data']['logical_total'], 12)

    def test_reboot_pending_is_warning_without_restart_or_registry_write(self):
        with patch.object(diagnostics, '_powershell', return_value={'component_servicing': True, 'windows_update': False, 'pending_file_rename': False}) as query:
            result = self.run_feature('f005')
        self.assertTrue(result['warnings'])
        self.assertIn('Test-Path', query.call_args.args[1])
        self.assertNotIn('Set-Item', query.call_args.args[1])
        self.assertNotIn('Restart-Computer', query.call_args.args[1])

    def test_disk_headroom_is_observed_from_installation_volume(self):
        usage = SimpleNamespace(total=20 * 1024**3, used=18 * 1024**3, free=2 * 1024**3)
        with patch.object(shutil, 'disk_usage', return_value=usage) as disk:
            result = self.run_feature('f003')
        disk.assert_called_once_with(self.root)
        self.assertEqual(result['data']['free_bytes'], usage.free)
        self.assertTrue(result['warnings'])


if __name__ == '__main__':
    unittest.main()
