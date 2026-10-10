import json,os,subprocess,sys,tempfile,time,unittest,urllib.request
from pathlib import Path
import app

class AllToolsLaunchTests(unittest.TestCase):
    def test_command_flag_selects_every_pack_in_status_and_actual_dashboard(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            process=subprocess.Popen([sys.executable,str(Path(app.__file__).resolve()),'--root',str(root),'--simulate','--no-browser','--all-tools'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            origin=None;headers=None
            try:
                session=root/'local-session.json';deadline=time.monotonic()+10
                while not session.is_file() and process.poll() is None and time.monotonic()<deadline:time.sleep(.05)
                self.assertTrue(session.is_file(),'all-tools command starts the protected dashboard')
                record=json.loads(session.read_text());origin='http://127.0.0.1:'+str(record['port'])
                headers={'X-Workbench-Token':record['token'],'Origin':origin,'Content-Type':'application/json'}
                with urllib.request.urlopen(urllib.request.Request(origin+'/api/status',headers=headers),timeout=5) as response:status=json.load(response)
                self.assertTrue(all(value for name,value in status['options'].items() if name!='live'))
                self.assertFalse(status['options']['live'],'Public one-click setup must not make an automatic model request.')
                self.assertIn('dotnet',[row['id'] for row in status['plan']])
                self.assertNotIn('live',[row['id'] for row in status['plan']])
                with urllib.request.urlopen(origin+'/',timeout=5) as response:html=response.read()
                self.assertIn(b'name="dotnet" checked>',html)
                self.assertNotIn(b'name="live" checked',html)
            finally:
                if origin:
                    with urllib.request.urlopen(urllib.request.Request(origin+'/api/quit',data=b'{}',headers=headers),timeout=5) as response:response.read()
                try:process.wait(timeout=8)
                except subprocess.TimeoutExpired:process.terminate();process.wait(timeout=5)
