import base64
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
            item=self.item('git')
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


class PackageRecoveryTests(unittest.TestCase):
    version='1.26.2734.0'
    digest='a'*64
    microsoft={'status':'Valid','subject':'CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US'}
    google={'status':'Valid','simple_name':'Google LLC','subject':'CN=Google LLC, O=Google LLC, L=Mountain View, S=California, C=US, SERIALNUMBER=3582691'}

    def workbench(self, root):
        workbench=engine.Workbench(Path(root));workbench.current_result={};workbench.arch='x64'
        return workbench

    def terminal_metadata(self):
        name='Microsoft.WindowsTerminalPreview_'+self.version+'_8wekyb3d8bbwe.msixbundle'
        return {'tag_name':'v'+self.version,'draft':False,'assets':[{'name':name,'digest':'sha256:'+self.digest,'browser_download_url':'https://github.com/microsoft/terminal/releases/download/v'+self.version+'/'+name}]}

    def terminal_registration(self, version=None):
        return [{'Name':'Microsoft.WindowsTerminalPreview','version':version or self.version,'status':'Ok'}]

    def canary_inspection(self, version=None, stable='154.0.8037.98'):
        target=r'C:\Users\test\AppData\Local\Google\Chrome SxS\Application\chrome.exe'
        return {'target_path':target,'target_scope':'user','executables':([{'path':target,'version':version,'signature':dict(self.google)}] if version else []),'registrations':[],'stable_executables':[{'path':r'C:\Program Files\Google\Chrome\Application\chrome.exe','version':stable}]}

    def canary_metadata(self, version='157.0.8095.0'):
        path='manifests/g/Google/Chrome/Canary/'+version+'/Google.Chrome.Canary.installer.yaml'
        manifest='\n'.join([
            'PackageIdentifier: Google.Chrome.Canary','PackageVersion: '+version,'InstallerType: exe','Scope: user',
            'InstallModes:','- silent','InstallerSwitches:','  Log: --verbose-logging --log-file="<LOGPATH>"','  Custom: --chrome-sxs --do-not-launch-chrome',
            'Installers:','- Architecture: x64','  InstallerUrl: https://dl.google.com/release2/chrome/verifiedhash_'+version+'/'+version+'_chrome_installer_uncompressed.exe',
            '  InstallerSha256: '+self.digest,'- Architecture: arm64','  InstallerUrl: https://dl.google.com/release2/chrome/armhash_'+version+'/'+version+'_chrome_installer_uncompressed.exe',
            '  InstallerSha256: '+'b'*64,'ManifestType: installer','ManifestVersion: 1.12.0',''])
        return {'path':path,'encoding':'base64','content':base64.b64encode(manifest.encode()).decode()}

    def test_terminal_exact_official_asset_hash_signature_and_registration(self):
        with tempfile.TemporaryDirectory() as root:
            workbench=self.workbench(root)
            with patch.object(workbench,'get_json',return_value=self.terminal_metadata()),patch.object(workbench,'fetch') as download,patch.object(workbench,'ps_json',side_effect=[dict(self.microsoft),self.terminal_registration()]) as native:
                result=workbench.install_terminal_preview_local(self.version)
            self.assertEqual(result,self.terminal_registration())
            self.assertEqual(download.call_args.args[2],self.digest)
            self.assertEqual(native.call_count,2)
            self.assertEqual(workbench.current_result['local_recovery']['version'],self.version)

    def test_terminal_metadata_failure_never_downloads_or_installs(self):
        changes=('missing_digest','wrong_tag','duplicate_asset','wrong_repository_url')
        for change in changes:
            with self.subTest(change=change),tempfile.TemporaryDirectory() as root:
                workbench=self.workbench(root);meta=self.terminal_metadata()
                if change=='missing_digest':meta['assets'][0].pop('digest')
                elif change=='wrong_tag':meta['tag_name']='v1.25.0.0'
                elif change=='duplicate_asset':meta['assets']*=2
                else:meta['assets'][0]['browser_download_url']='https://github.com/other/project/payload.msixbundle'
                with patch.object(workbench,'get_json',return_value=meta),patch.object(workbench,'fetch') as download,patch.object(workbench,'ps_json') as native:
                    with self.assertRaises(engine.OperationError):workbench.install_terminal_preview_local(self.version)
                download.assert_not_called();native.assert_not_called()

    def test_terminal_wrong_signature_prevents_mutating_command(self):
        with tempfile.TemporaryDirectory() as root:
            workbench=self.workbench(root)
            with patch.object(workbench,'get_json',return_value=self.terminal_metadata()),patch.object(workbench,'fetch'),patch.object(workbench,'ps_json',return_value={'status':'Valid','subject':'CN=Someone Else'}) as native:
                with self.assertRaisesRegex(engine.OperationError,'Microsoft Corporation signature'):workbench.install_terminal_preview_local(self.version)
            self.assertEqual(native.call_count,1)

    def test_terminal_post_install_wrong_version_is_not_verified(self):
        with tempfile.TemporaryDirectory() as root:
            workbench=self.workbench(root)
            with patch.object(workbench,'get_json',return_value=self.terminal_metadata()),patch.object(workbench,'fetch'),patch.object(workbench,'ps_json',side_effect=[dict(self.microsoft),self.terminal_registration('1.25.0.0')]):
                with self.assertRaisesRegex(engine.OperationError,'exact Preview AppX'):workbench.install_terminal_preview_local(self.version)

    def test_terminal_stop_during_download_prevents_local_install(self):
        with tempfile.TemporaryDirectory() as root:
            workbench=self.workbench(root)
            with patch.object(workbench,'get_json',return_value=self.terminal_metadata()),patch.object(workbench,'fetch',side_effect=lambda *args,**kwargs:workbench.cancel.set()),patch.object(workbench,'ps_json',return_value=dict(self.microsoft)) as native:
                with self.assertRaises(engine.StopRun):workbench.install_terminal_preview_local(self.version)
            self.assertEqual(native.call_count,1)

    def test_terminal_only_completed_three_timeouts_trigger_local_recovery(self):
        with tempfile.TemporaryDirectory() as root:
            workbench=self.workbench(root)
            item=next(item for item in engine.build_plan(engine.default_options()) if item['id']=='terminal')
            results=[engine.CommandResult(1,'missing'),engine.CommandResult(0,self.version)]+[engine.CommandResult(0x80072EE2,'timeout')]*3+[engine.CommandResult(1,'inventory still unavailable')]
            with patch.object(workbench,'find',return_value='winget.exe'),patch.object(workbench,'refresh_path'),patch.object(workbench.cancel,'wait',return_value=False),patch.object(workbench,'run_command',side_effect=results) as commands,patch.object(workbench,'install_terminal_preview_local',return_value=self.terminal_registration()) as recovery:
                workbench.install_winget(item)
            recovery.assert_called_once_with(self.version)
            self.assertEqual(commands.call_count,6)
            self.assertEqual(workbench.current_result['status'],'VERIFIED')

    def test_terminal_killed_manager_never_triggers_local_recovery(self):
        with tempfile.TemporaryDirectory() as root:
            workbench=self.workbench(root)
            item=next(item for item in engine.build_plan(engine.default_options()) if item['id']=='terminal')
            results=[engine.CommandResult(1,'missing'),engine.CommandResult(0,self.version),engine.CommandResult(-2,'manager killed',True)]
            with patch.object(workbench,'find',return_value='winget.exe'),patch.object(workbench,'run_command',side_effect=results),patch.object(workbench,'install_terminal_preview_local') as recovery:
                with self.assertRaises(engine.StopRun):workbench.install_winget(item)
            recovery.assert_not_called()

    def test_canary_manifest_selects_exact_architecture_and_preserves_stable(self):
        with tempfile.TemporaryDirectory() as root:
            workbench=self.workbench(root);workbench.arch='arm64'
            before=self.canary_inspection();after=self.canary_inspection('157.0.8095.0')
            with patch.object(workbench,'get_json',return_value=self.canary_metadata()),patch.object(workbench,'fetch') as download,patch.object(workbench,'ps_json',return_value=dict(self.google)),patch.object(workbench,'ps',return_value=engine.CommandResult(0,'CANARY_INSTALL_COMPLETED')),patch.object(workbench,'canary_registration',return_value=after):
                workbench.install_canary_local('157.0.8095.0',before)
            self.assertIn('/armhash_',download.call_args.args[0])
            self.assertEqual(download.call_args.args[2],'b'*64)
            self.assertEqual(workbench.current_result['channel_install']['switches'],['--chrome-sxs','--do-not-launch-chrome'])

    def test_canary_ambiguous_or_changed_manifest_never_downloads(self):
        changes=('wrong_identity','wrong_scope','wrong_switches','wrong_host','duplicate_architecture')
        for change in changes:
            with self.subTest(change=change),tempfile.TemporaryDirectory() as root:
                workbench=self.workbench(root);meta=self.canary_metadata()
                manifest=base64.b64decode(meta['content']).decode()
                if change=='wrong_identity':manifest=manifest.replace('PackageIdentifier: Google.Chrome.Canary','PackageIdentifier: Google.Chrome')
                elif change=='wrong_scope':manifest=manifest.replace('Scope: user','Scope: machine')
                elif change=='wrong_switches':manifest=manifest.replace('--chrome-sxs --do-not-launch-chrome','--make-default-browser')
                elif change=='wrong_host':manifest=manifest.replace('https://dl.google.com/','https://evil.example/')
                else:manifest=manifest.replace('- Architecture: arm64','- Architecture: x64')
                meta['content']=base64.b64encode(manifest.encode()).decode()
                with patch.object(workbench,'get_json',return_value=meta),patch.object(workbench,'fetch') as download,patch.object(workbench,'ps') as native:
                    with self.assertRaises(engine.OperationError):workbench.install_canary_local('157.0.8095.0',self.canary_inspection())
                download.assert_not_called();native.assert_not_called()

    def test_canary_wrong_google_signer_never_runs_installer(self):
        with tempfile.TemporaryDirectory() as root:
            workbench=self.workbench(root)
            wrong={'status':'Valid','simple_name':'Other Company','subject':'CN=Other Company, O=Other Company'}
            with patch.object(workbench,'get_json',return_value=self.canary_metadata()),patch.object(workbench,'fetch'),patch.object(workbench,'ps_json',return_value=wrong),patch.object(workbench,'ps') as native:
                with self.assertRaisesRegex(engine.OperationError,'Google LLC signer'):workbench.install_canary_local('157.0.8095.0',self.canary_inspection())
            native.assert_not_called()

    def test_canary_wrong_binary_version_and_changed_stable_are_not_success(self):
        for after in (self.canary_inspection('156.0.8095.0'),self.canary_inspection('157.0.8095.0','155.0.8037.98')):
            with self.subTest(after=after),tempfile.TemporaryDirectory() as root:
                workbench=self.workbench(root)
                with patch.object(workbench,'get_json',return_value=self.canary_metadata()),patch.object(workbench,'fetch'),patch.object(workbench,'ps_json',return_value=dict(self.google)),patch.object(workbench,'ps',return_value=engine.CommandResult(0,'CANARY_INSTALL_COMPLETED')),patch.object(workbench,'canary_registration',return_value=after):
                    with self.assertRaises(engine.OperationError):workbench.install_canary_local('157.0.8095.0',self.canary_inspection())

    def test_canary_stop_during_download_never_runs_installer(self):
        with tempfile.TemporaryDirectory() as root:
            workbench=self.workbench(root)
            with patch.object(workbench,'get_json',return_value=self.canary_metadata()),patch.object(workbench,'fetch',side_effect=lambda *args,**kwargs:workbench.cancel.set()),patch.object(workbench,'ps_json',return_value=dict(self.google)),patch.object(workbench,'ps') as native:
                with self.assertRaises(engine.StopRun):workbench.install_canary_local('157.0.8095.0',self.canary_inspection())
            native.assert_not_called()

    def test_canary_handler_uses_actual_user_binary_not_stable_correlation(self):
        with tempfile.TemporaryDirectory() as root:
            workbench=self.workbench(root)
            item=next(item for item in engine.build_plan(engine.default_options()) if item['id']=='canary')
            results=[engine.CommandResult(0,'Google Chrome Google.Chrome.Canary 154.0.8037.98'),engine.CommandResult(0,'157.0.8095.0')]
            inspection=self.canary_inspection('157.0.8095.0')
            inspection['executables'].append({'path':r'C:\Program Files\Google\Chrome SxS\Application\chrome.exe','version':'158.0.0.0','signature':dict(self.google)})
            with patch.object(workbench,'find',return_value='winget.exe'),patch.object(workbench,'run_command',side_effect=results) as commands,patch.object(workbench,'canary_registration',return_value=inspection),patch.object(workbench,'install_canary_local') as install:
                workbench.install_winget(item)
            install.assert_not_called();self.assertEqual(commands.call_count,2)
            self.assertEqual(workbench.current_result['status'],'VERIFIED')
            self.assertEqual(workbench.current_result['actual'],'157.0.8095.0')
            self.assertEqual(workbench.current_result['winget_correlated_before'],'154.0.8037.98')
            self.assertIn('Per-user',workbench.current_result['detail'])

    def test_newer_existing_canary_is_preserved_without_downgrade(self):
        with tempfile.TemporaryDirectory() as root:
            workbench=self.workbench(root)
            item=next(item for item in engine.build_plan(engine.default_options()) if item['id']=='canary')
            results=[engine.CommandResult(0,'Google Chrome Google.Chrome.Canary 154.0.8037.98'),engine.CommandResult(0,'157.0.8095.0')]
            with patch.object(workbench,'find',return_value='winget.exe'),patch.object(workbench,'run_command',side_effect=results),patch.object(workbench,'canary_registration',return_value=self.canary_inspection('158.0.0.0')),patch.object(workbench,'install_canary_local') as install:
                workbench.install_winget(item)
            install.assert_not_called();self.assertEqual(workbench.current_result['status'],'INSTALLED_CHECK_NEEDED')
            self.assertEqual(workbench.current_result['actual'],'158.0.0.0')

    def test_unsigned_existing_canary_is_preserved_for_review(self):
        inspection=self.canary_inspection('157.0.8095.0');inspection['executables'][0]['signature']['status']='NotSigned'
        with self.assertRaisesRegex(engine.OperationError,'preserved for review'):engine.Workbench.canary_user_binary(inspection)

    def test_canary_missing_catalog_is_honestly_unverified_without_mutation(self):
        with tempfile.TemporaryDirectory() as root:
            workbench=self.workbench(root)
            item=next(item for item in engine.build_plan(engine.default_options()) if item['id']=='canary')
            results=[engine.CommandResult(0,'Google Chrome Google.Chrome.Canary 154.0.8037.98'),engine.CommandResult(1,'catalog unavailable')]
            with patch.object(workbench,'find',return_value='winget.exe'),patch.object(workbench,'run_command',side_effect=results),patch.object(workbench,'canary_registration',return_value=self.canary_inspection()),patch.object(workbench,'install_canary_local') as install:
                workbench.install_winget(item)
            install.assert_not_called();self.assertEqual(workbench.current_result['status'],'CHANNEL_NOT_VERIFIED')


if __name__=='__main__':
    unittest.main()
