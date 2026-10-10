import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import json
import engine

class NpmMetadataTests(unittest.TestCase):
    nightly='v27.0.0-nightly202610086d5e309871'
    host='v26.11.1'
    warning='npm warn cli npm v12.1.0 does not support Node.js '+nightly

    def test_warning_is_preserved_separately_from_version(self):
        self.assertEqual(engine.Workbench.npm_version_output(self.warning+'\n12.1.0'),('12.1.0',[self.warning]))

    def test_plain_prerelease_version_does_not_create_warning(self):
        self.assertEqual(engine.Workbench.npm_version_output('\n\x1b[0m\n12.2.0-beta.1\n'),('12.2.0-beta.1',[]))

    def test_warning_without_actual_version_fails(self):
        with self.assertRaises(engine.OperationError):engine.Workbench.npm_version_output(self.warning)

    def test_multiple_version_lines_fail(self):
        with self.assertRaises(engine.OperationError):engine.Workbench.npm_version_output('12.1.0\n12.2.0')

    def exercise(self,root,*,warning=False,choice=None,cancel=False):
        w=engine.Workbench(Path(root));w.arch='x64';w.current_result={'status':'RUNNING'}
        old={'version':'previous','command':['previous']};w.active={'node':old,'npm':old}
        night=w.root/'night/node.exe';host=w.root/'host/node.exe'
        for exe in (night,host):
            exe.parent.mkdir();exe.touch();semver=exe.parent/'node_modules/npm/node_modules/semver';semver.mkdir(parents=True);(semver/'index.js').touch()
        npm=w.root/'runtimes/npm/12.2.0';entry=npm/'node_modules/npm/bin/npm-cli.js';entry.parent.mkdir(parents=True);entry.touch()
        (npm/'.workbench-owned.json').write_text(json.dumps({'owned_by':engine.SCHEMA,'version':'12.2.0'}))
        meta={'name':'npm','versions':{'12.2.0':{'engines':{'node':'>=26.0.0'}}}}
        results=[engine.CommandResult(0,json.dumps(choice or {'host':self.host,'nightly_accepted':False})),engine.CommandResult(0,'11.20.0'),engine.CommandResult(0,(self.warning+'\n' if warning else '')+'12.2.0')]
        if cancel:w.cancel.set()
        with patch.object(w,'get_json',side_effect=[[{'version':self.nightly,'files':['win-x64-zip']}],[{'version':self.host,'files':['win-x64-zip']}]]),patch.object(w,'npm_meta',return_value=meta),patch.object(w,'node_archive',side_effect=[night,host]),patch.object(w,'run_command',side_effect=results):
            try:w.step_node()
            except (engine.OperationError,engine.StopRun) as exc:return w,exc
        return w,None

    def test_newest_nightly_kept_with_explicit_compatible_npm_host(self):
        with tempfile.TemporaryDirectory() as root:
            w,error=self.exercise(root)
            self.assertIsNone(error);self.assertEqual(w.active['node']['version'],self.nightly)
            self.assertEqual(w.active['npm']['host_version'],self.host);self.assertEqual(w.active['npm']['version'],'12.2.0')
            self.assertEqual(w.active['npm']['diagnostics'],[])
            self.assertIn(str(Path(w.active['npm']['command'][0]).parent),w.npm_environment()['PATH'])

    def test_actual_warning_rejects_candidate_without_replacing_previous_pair(self):
        with tempfile.TemporaryDirectory() as root:
            w,error=self.exercise(root,warning=True)
            self.assertIsInstance(error,engine.OperationError);self.assertEqual(w.active['node']['version'],'previous');self.assertEqual(w.active['npm']['version'],'previous')

    def test_unpublished_host_is_rejected_before_activation(self):
        with tempfile.TemporaryDirectory() as root:
            w,error=self.exercise(root,choice={'host':'v99.0.0','nightly_accepted':False})
            self.assertIsInstance(error,engine.OperationError);self.assertEqual(w.active['node']['version'],'previous')

    def test_cancel_keeps_previous_pair(self):
        with tempfile.TemporaryDirectory() as root:
            w,error=self.exercise(root,cancel=True)
            self.assertIsInstance(error,engine.StopRun);self.assertEqual(w.active['npm']['version'],'previous')

if __name__=='__main__':unittest.main()
