import json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import engine

class RegressionTests(unittest.TestCase):
    def test_combined_alpha_platform_package_is_not_a_channel(self):
        self.assertEqual(engine.choose_npm({'versions':{'1.3.0-alpha.4-linux-x64':{},'1.2.0-alpha.2':{}}}), '1.2.0-alpha.2')
    def test_target_symlink_does_not_redirect_settings_copy(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t); a=p/'a'; b=p/'b'; out=p/'outside'
            (a/'snippets').mkdir(parents=True); b.mkdir();out.mkdir()
            (a/'snippets'/'code.json').write_text('private')
            (b/'snippets').symlink_to(out,target_is_directory=True)
            result=engine.merge_missing(a,b)
            self.assertFalse((out/'code.json').exists())
            self.assertIn('snippets/code.json',result['skipped'])
    def test_process_start_failure_records_evidence(self):
        with tempfile.TemporaryDirectory() as t:
            w=engine.Workbench(Path(t));w.current_result={}
            r=w.run_command(['/no-such-workbench-program'])
            self.assertNotEqual(r.code,0)
            self.assertEqual(w.current_result['commands'][0]['exit_code'],-1)
    def test_incremental_reports_are_valid_json_and_redacted(self):
        with tempfile.TemporaryDirectory() as t:
            w=engine.Workbench(Path(t)); w.report['checks']['test']='Bearer private123token'
            w.write_report(final=False)
            data=json.loads((w.run_dir/'Diagnostic.json').read_text())
            self.assertFalse(data['final']);self.assertNotIn('private123token',str(data))
    def test_simulated_run_is_never_reported_verified(self):
        with tempfile.TemporaryDirectory() as t:
            w=engine.Workbench(Path(t),simulate=True);w.plan=engine.build_plan(engine.default_options())
            w.execute()
            self.assertTrue(w.finished)
            self.assertEqual({x['status'] for x in w.results},{'SIMULATED'})
    def test_cleanup_leaves_unowned_directories(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);w=engine.Workbench(root);w.current_result={}
            for n in range(4):
                d=root/'runtimes'/'node'/str(n);d.mkdir(parents=True)
                (d/'keep.txt').write_text('keep')
            w.step_cleanup()
            self.assertEqual(len(list((root/'runtimes'/'node').iterdir())),4)

if __name__=='__main__':unittest.main()
