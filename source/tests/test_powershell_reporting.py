import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import engine


class PowerShellReportingTests(unittest.TestCase):
    def test_empty_success_output_is_a_named_failure(self):
        with tempfile.TemporaryDirectory() as t:
            w=engine.Workbench(Path(t))
            with patch.object(w,'ps',return_value=engine.CommandResult(0,'')):
                with self.assertRaisesRegex(engine.OperationError,'Back up original user PATH did not return valid JSON'):
                    w.ps_json('ignored',label='Back up original user PATH')

    def test_failed_query_cannot_be_parsed_as_success(self):
        with tempfile.TemporaryDirectory() as t:
            w=engine.Workbench(Path(t))
            with patch.object(w,'ps',return_value=engine.CommandResult(1,'module failure')):
                with self.assertRaisesRegex(engine.OperationError,'failed'):
                    w.ps_json('ignored',label='PATH query')

    @unittest.skipUnless(os.name=='nt','Real Windows PowerShell contract')
    def test_json_with_ps7_module_search_path(self):
        with tempfile.TemporaryDirectory() as t:
            w=engine.Workbench(Path(t));w.current_result={}
            w.env['PSModulePath']=str(Path(os.environ.get('ProgramFiles',r'C:\Program Files'))/'PowerShell'/'7'/'Modules')
            data=w.ps_json("[pscustomobject]@{path='C:\\Example;C:\\Other';empty=$null} | ConvertTo-Json -Compress",label='JSON contract')
            self.assertEqual(data,{'path':'C:\\Example;C:\\Other','empty':None})
            failed=w.ps("throw 'EXPECTED_FAILURE'",label='Failure contract')
            self.assertNotEqual(failed.code,0)
            self.assertIn('EXPECTED_FAILURE',failed.out)

    @unittest.skipUnless(os.name=='nt','Windows user PATH handling')
    def test_bad_backup_output_never_updates_path(self):
        with tempfile.TemporaryDirectory() as t:
            w=engine.Workbench(Path(t));w.current_result={}
            with patch.object(w,'ps',return_value=engine.CommandResult(0,'')) as ps:
                with self.assertRaises(engine.OperationError):w.step_report()
            self.assertEqual(ps.call_count,1)
            self.assertFalse((w.root/'private-backups'/'user-path-before-workbench.json').exists())

    @unittest.skipUnless(os.name=='nt','Windows user PATH handling')
    def test_invalid_existing_backup_never_updates_path(self):
        with tempfile.TemporaryDirectory() as t:
            w=engine.Workbench(Path(t));w.current_result={}
            engine.atomic_json(w.root/'private-backups'/'user-path-before-workbench.json',{'wrong':'value'})
            with patch.object(w,'ps') as ps:
                with self.assertRaises(engine.OperationError):w.step_report()
            ps.assert_not_called()

    @unittest.skipUnless(os.name=='nt','Windows user PATH handling')
    def test_report_retains_original_path_backup_on_rerun(self):
        with tempfile.TemporaryDirectory() as t:
            w=engine.Workbench(Path(t));w.current_result={}
            previous=w.root/'private-backups'/'user-path-before-workbench.json'
            engine.atomic_json(previous,{'path':'C:\\Original'})
            with patch.object(w,'ps',return_value=engine.CommandResult(0,'USER_PATH_UPDATED')):
                w.step_report();w.step_report()
            self.assertEqual(json.loads(previous.read_text()),{'path':'C:\\Original'})
            self.assertTrue(w.report['checks']['user_path_update']['passed'])


if __name__=='__main__':unittest.main()
