import tempfile,unittest,json,sys
from pathlib import Path
from unittest.mock import patch
import engine

class AdapterTests(unittest.TestCase):
    def workbench(self,t):
        w=engine.Workbench(Path(t));w.current_result={};return w
    def test_successful_installer_missing_registration_is_failure(self):
        with tempfile.TemporaryDirectory() as t:
            w=self.workbench(t);item=next(x for x in engine.build_plan(engine.default_options()) if x['id']=='git')
            responses=[engine.CommandResult(1,'not installed'),engine.CommandResult(0,'2.60.0'),engine.CommandResult(0,'installed'),engine.CommandResult(1,'missing')]
            with patch.object(w,'find',return_value='winget.exe'),patch.object(w,'refresh_path'),patch.object(w,'run_command',side_effect=responses):
                with self.assertRaises(engine.OperationError):w.install_winget(item)
    def test_installer_and_exact_registered_version_are_verified(self):
        with tempfile.TemporaryDirectory() as t:
            w=self.workbench(t);item=next(x for x in engine.build_plan(engine.default_options()) if x['id']=='git')
            responses=[engine.CommandResult(1,'not installed'),engine.CommandResult(0,'2.60.0'),engine.CommandResult(0,'installed'),engine.CommandResult(0,'Git Git.Git 2.60.0 winget')]
            with patch.object(w,'find',return_value='winget.exe'),patch.object(w,'refresh_path'),patch.object(w,'run_command',side_effect=responses):w.install_winget(item)
            self.assertEqual(w.current_result['status'],'VERIFIED')
    def test_new_version_mismatch_is_not_verified(self):
        with tempfile.TemporaryDirectory() as t:
            w=self.workbench(t);item=next(x for x in engine.build_plan(engine.default_options()) if x['id']=='git')
            responses=[engine.CommandResult(1,'not installed'),engine.CommandResult(0,'2.60.0'),engine.CommandResult(0,'installed'),engine.CommandResult(0,'Git Git.Git 2.59.0 winget')]
            with patch.object(w,'find',return_value='winget.exe'),patch.object(w,'refresh_path'),patch.object(w,'run_command',side_effect=responses):w.install_winget(item)
            self.assertEqual(w.current_result['status'],'INSTALLED_CHECK_NEEDED')
    def test_real_child_output_and_nonzero_exit_evidence(self):
        with tempfile.TemporaryDirectory() as t:
            w=self.workbench(t)
            r=w.run_command([sys.executable,'-c',"print('EVIDENCE_OK');raise SystemExit(3)"],label='test child')
            self.assertEqual(r.code,3);self.assertIn('EVIDENCE_OK',r.out)
            self.assertEqual(w.current_result['commands'][0]['exit_code'],3)
    def test_rerun_options_cannot_start_second_worker(self):
        with tempfile.TemporaryDirectory() as t:
            w=self.workbench(t);w.started=True
            self.assertFalse(w.start(engine.default_options()))

if __name__=='__main__':unittest.main()
