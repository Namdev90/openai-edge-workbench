import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import engine


class WindowsPackageTests(unittest.TestCase):
    def workbench(self, root):
        workbench=engine.Workbench(Path(root))
        workbench.current_result={}
        return workbench

    def item(self, name='powershell'):
        return next(item for item in engine.build_plan(engine.default_options()) if item['id']==name)

    def test_transient_installer_timeout_retries_exact_same_package_channel(self):
        with tempfile.TemporaryDirectory() as root:
            workbench=self.workbench(root)
            item=self.item()
            results=[engine.CommandResult(1,'missing'),engine.CommandResult(0,'7.7.5.0'),
                     engine.CommandResult(0x80072EE2,'dependency download timed out'),
                     engine.CommandResult(0,'installed'),
                     engine.CommandResult(0,item['package']+' 7.7.5.0')]
            with patch.object(workbench,'find',return_value='winget.exe'),patch.object(workbench,'refresh_path'),patch.object(workbench.cancel,'wait',return_value=False) as delay,patch.object(workbench,'run_command',side_effect=results) as commands:
                workbench.install_winget(item)
            self.assertEqual(commands.call_args_list[2].args,commands.call_args_list[3].args)
            self.assertNotIn('--ignore-security-hash',commands.call_args_list[3].args[0])
            self.assertNotIn('--skip-dependencies',commands.call_args_list[3].args[0])
            self.assertEqual(workbench.current_result['status'],'VERIFIED')
            self.assertEqual(workbench.current_result['retries'][0]['channel'],'Preview')
            delay.assert_called_once_with(5)

    def test_timeout_retry_limit_is_three_attempts_including_signed_hresult(self):
        with tempfile.TemporaryDirectory() as root:
            workbench=self.workbench(root)
            results=[engine.CommandResult(1,'missing'),engine.CommandResult(0,'7.7.5.0')]+[engine.CommandResult(-2147012894,'0x80072ee2')]*3
            with patch.object(workbench,'find',return_value='winget.exe'),patch.object(workbench.cancel,'wait',return_value=False) as delay,patch.object(workbench,'run_command',side_effect=results) as commands:
                with self.assertRaises(engine.OperationError):workbench.install_winget(self.item())
            self.assertEqual(commands.call_count,5)
            self.assertEqual([call.args[0] for call in delay.call_args_list],[5,15])

    def test_security_failure_with_timeout_text_is_never_retried(self):
        with tempfile.TemporaryDirectory() as root:
            workbench=self.workbench(root)
            results=[engine.CommandResult(1,'missing'),engine.CommandResult(0,'7.7.5.0'),engine.CommandResult(0x8A15002D,'Security failure; previous diagnostic: 0x80072ee2')]
            with patch.object(workbench,'find',return_value='winget.exe'),patch.object(workbench.cancel,'wait') as delay,patch.object(workbench,'run_command',side_effect=results):
                with self.assertRaises(engine.OperationError):workbench.install_winget(self.item())
            delay.assert_not_called()

    def test_killed_manager_timeout_is_not_retried(self):
        with tempfile.TemporaryDirectory() as root:
            workbench=self.workbench(root)
            results=[engine.CommandResult(1,'missing'),engine.CommandResult(0,'7.7.5.0'),engine.CommandResult(-2,'',True)]
            with patch.object(workbench,'find',return_value='winget.exe'),patch.object(workbench.cancel,'wait') as delay,patch.object(workbench,'run_command',side_effect=results):
                with self.assertRaises(engine.StopRun):workbench.install_winget(self.item())
            delay.assert_not_called()

    def test_cancel_interrupts_retry_delay_without_another_mutation(self):
        with tempfile.TemporaryDirectory() as root:
            workbench=self.workbench(root)
            results=[engine.CommandResult(1,'missing'),engine.CommandResult(0,'7.7.5.0'),engine.CommandResult(0x80072EE2,'timeout')]
            with patch.object(workbench,'find',return_value='winget.exe'),patch.object(workbench.cancel,'wait',return_value=True),patch.object(workbench,'run_command',side_effect=results) as commands:
                with self.assertRaises(engine.StopRun):workbench.install_winget(self.item())
            self.assertEqual(commands.call_count,3)

    def test_no_applicable_update_with_known_different_version_is_mismatch(self):
        with tempfile.TemporaryDirectory() as root:
            workbench=self.workbench(root)
            item=self.item('canary')
            results=[engine.CommandResult(0,item['package']+' 154.0.4203.0'),engine.CommandResult(0,'157.0.4535.0'),engine.CommandResult(0x8A15002B,'No applicable update'),engine.CommandResult(0,item['package']+' 154.0.4203.0')]
            with patch.object(workbench,'find',return_value='winget.exe'),patch.object(workbench,'refresh_path'),patch.object(workbench,'run_command',side_effect=results):
                workbench.install_winget(item)
            self.assertEqual(workbench.current_result['status'],'VERSION_MISMATCH')
            self.assertIn('154.0.4203.0',workbench.current_result['detail'])
            self.assertIn('157.0.4535.0',workbench.current_result['detail'])

    def test_no_applicable_update_without_catalog_version_remains_qualified(self):
        with tempfile.TemporaryDirectory() as root:
            workbench=self.workbench(root)
            item=self.item()
            results=[engine.CommandResult(0,item['package']+' 7.7.5.0'),engine.CommandResult(0,'catalog target unknown'),engine.CommandResult(0x8A15002B,'No applicable update'),engine.CommandResult(0,item['package']+' 7.7.5.0')]
            with patch.object(workbench,'find',return_value='winget.exe'),patch.object(workbench,'refresh_path'),patch.object(workbench,'run_command',side_effect=results):
                workbench.install_winget(item)
            self.assertEqual(workbench.current_result['status'],'CATALOG_CURRENT')
            self.assertIn('not proved',workbench.current_result['detail'])

    def test_hidden_webview_registration_is_verified_without_winget_inventory(self):
        with tempfile.TemporaryDirectory() as root:
            workbench=self.workbench(root)
            item=self.item('webview')
            results=[engine.CommandResult(1,'missing'),engine.CommandResult(0,'154.0.4203.0'),engine.CommandResult(0,'installed'),engine.CommandResult(1,'No installed package')]
            registration=[{'location':'HKEY_LOCAL_MACHINE\\SOFTWARE\\WOW6432Node\\Microsoft\\EdgeUpdate\\Clients\\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}','version':'154.0.4203.0'}]
            with patch.object(workbench,'find',return_value='winget.exe'),patch.object(workbench,'refresh_path'),patch.object(workbench,'webview_registration',return_value=registration),patch.object(workbench,'run_command',side_effect=results):
                workbench.install_winget(item)
            self.assertEqual(workbench.current_result['status'],'VERIFIED')
            self.assertEqual(workbench.current_result['actual'],'154.0.4203.0')
            self.assertEqual(workbench.current_result['registration_check']['winget_inventory_exit_code'],1)

    def test_webview_missing_official_registration_is_not_false_success(self):
        with tempfile.TemporaryDirectory() as root:
            workbench=self.workbench(root)
            item=self.item('webview')
            results=[engine.CommandResult(1,'missing'),engine.CommandResult(0,'154.0.4203.0'),engine.CommandResult(0,'installed'),engine.CommandResult(0,item['package']+' 154.0.4203.0')]
            with patch.object(workbench,'find',return_value='winget.exe'),patch.object(workbench,'refresh_path'),patch.object(workbench,'webview_registration',return_value=[]),patch.object(workbench,'run_command',side_effect=results):
                with self.assertRaisesRegex(engine.OperationError,'neither'):workbench.install_winget(item)

    def test_webview_registry_rejects_null_zero_and_malformed_versions(self):
        with tempfile.TemporaryDirectory() as root:
            workbench=self.workbench(root)
            rows=[{'version':value} for value in ('','0.0.0.0',None,'154.0.4203.0','12.2.3','bad')]
            with patch.object(workbench,'ps',return_value=engine.CommandResult(0,json.dumps(rows))) as query:
                registrations=workbench.webview_registration()
            self.assertEqual(registrations,[{'version':'154.0.4203.0'}])
            body=query.call_args.args[0]
            self.assertIn("Hive='LocalMachine';View='Registry32'",body)
            self.assertIn("Hive='CurrentUser';View='Default'",body)
            self.assertIn("GetValue('pv'",body)

    def test_webview_registry_query_invalid_json_has_clear_failure(self):
        with tempfile.TemporaryDirectory() as root:
            workbench=self.workbench(root)
            with patch.object(workbench,'ps',return_value=engine.CommandResult(0,'')):
                with self.assertRaisesRegex(engine.OperationError,'invalid JSON'):workbench.webview_registration()


if __name__=='__main__':
    unittest.main()
