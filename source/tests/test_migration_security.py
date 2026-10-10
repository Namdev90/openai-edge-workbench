import json, os, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import engine
from test_regressions import directory_link

class MigrationSecurityTests(unittest.TestCase):
    def test_managed_root_junction_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); outside=root/'outside'; outside.mkdir()
            directory_link(root/'managed',outside)
            with self.assertRaises(ValueError):engine.Workbench(root/'managed')
            self.assertEqual(list(outside.iterdir()),[])

    def test_nested_junction_generation_retained(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); w=engine.Workbench(root);w.current_result={}
            outside=root/'outside';outside.mkdir();(outside/'user.txt').write_text('keep')
            for n in range(4):
                p=root/'runtimes/node'/str(n);p.mkdir(parents=True)
                engine.atomic_json(p/'.workbench-owned.json',{'owned_by':engine.SCHEMA})
                os.utime(p,(100+n,100+n))
            directory_link(root/'runtimes/node/0/link',outside)
            os.utime(root/'runtimes/node/0',(100,100))
            w.step_cleanup()
            self.assertTrue((root/'runtimes/node/0').exists())
            self.assertFalse((root/'runtimes/node/1').exists())
            self.assertEqual((outside/'user.txt').read_text(),'keep')

    def test_failed_python_candidate_preserves_active_environment(self):
        with tempfile.TemporaryDirectory() as t:
            w=engine.Workbench(Path(t));w.current_result={}
            previous={'version':'old','command':['old-python.exe']}
            w.active['python']=previous
            w.python_candidate={'version':'new','command':['new-python.exe']}
            w.python_candidate_failed=True
            with patch.object(w,'run_command') as run:w.activate_candidates()
            run.assert_not_called()
            self.assertEqual(w.active['python'],previous)
            self.assertEqual(json.loads(w.state_file.read_text())['tools']['python'],previous)

    def test_failed_sdk_import_preserves_python(self):
        with tempfile.TemporaryDirectory() as t:
            w=engine.Workbench(Path(t));w.current_result={}
            w.active['python']={'version':'old','command':['old.exe']}
            w.python_candidate={'version':'new','command':['new.exe']}
            with patch.object(w,'run_command',return_value=engine.CommandResult(1,'import failed')):w.activate_candidates()
            self.assertEqual(w.active['python']['version'],'old')
            self.assertTrue(w.python_candidate_failed)

    def test_successful_candidates_activate_after_checks(self):
        with tempfile.TemporaryDirectory() as t:
            w=engine.Workbench(Path(t));w.current_result={}
            w.python_candidate={'version':'new','command':['new.exe']}
            w.js_candidate={'path':'new-js','versions':{'openai':'new'}}
            with patch.object(w,'run_command',return_value=engine.CommandResult(0,'SDK_IMPORT_OK')):w.activate_candidates()
            self.assertEqual(w.active['python']['version'],'new')
            self.assertEqual(w.active['javascript']['path'],'new-js')

    def test_failed_javascript_set_preserves_previous_sdk_state(self):
        with tempfile.TemporaryDirectory() as t:
            w=engine.Workbench(Path(t));w.current_result={}
            previous={'path':'previous','versions':{'openai':'1.0.0'}};w.active['javascript']=previous
            with patch.object(w,'npm_meta',return_value={'versions':{'2.0.0-alpha.1':{}}}),patch.object(w,'npm_command',return_value=['node.exe','npm.js']),patch.object(w,'run_command',return_value=engine.CommandResult(1,'unsupported preview')):
                with self.assertRaises(engine.OperationError):w.install_js_packages(['openai'])
            self.assertEqual(w.active['javascript'],previous)
            self.assertTrue(w.js_candidate_failed)

if __name__=='__main__':unittest.main()
