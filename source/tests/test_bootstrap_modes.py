"""A real failed verification must exit without leaving a modal window open."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class BootstrapModeTests(unittest.TestCase):
    @unittest.skipUnless(os.name == 'nt' and shutil.which('powershell.exe'), 'Requires Windows PowerShell')
    def test_no_launch_failure_returns_nonzero_without_modal_ui_or_installation(self):
        bootstrap=Path(__file__).resolve().parents[1]/'bootstrap.ps1'
        environment=dict(os.environ,PROCESSOR_ARCHITECTURE='UNSUPPORTED_TEST_ARCH',PROCESSOR_ARCHITEW6432='')
        with tempfile.TemporaryDirectory(prefix='edge-bootstrap-failure-') as root:
            result=subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',
                                   str(bootstrap),'-Root',root,'-NoLaunch'],
                                  env=environment,capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,1,result.stdout+result.stderr)
            self.assertIn('BOOTSTRAP FAILED',result.stdout)
            diagnostic=(Path(root)/'Bootstrap-Diagnostic.txt').read_text(encoding='utf-8-sig')
            self.assertIn('64-bit Windows x64 or ARM64 is required',diagnostic)
            self.assertNotIn('NO_LAUNCH_VERIFICATION_OK',diagnostic)
            self.assertEqual({p.name for p in Path(root).iterdir()},{'Bootstrap-Diagnostic.txt'})
