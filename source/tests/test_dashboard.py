import http.client,json,tempfile,threading,time,unittest
from pathlib import Path
from unittest.mock import patch
import app
import engine

class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.w=engine.Workbench(Path(self.temp.name),simulate=True)
        self.server=app.make_server(self.w,token='test-capability')
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.port=self.server.server_address[1];self.origin=f'http://127.0.0.1:{self.port}'
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join(2)
        deadline=time.monotonic()+5
        while self.w.started and not self.w.finished and time.monotonic()<deadline:time.sleep(.02)
        self.temp.cleanup()
    def request(self,method,path,body=None,token=True,origin=None,host=None):
        conn=http.client.HTTPConnection('127.0.0.1',self.port,timeout=3)
        headers={}
        if token:headers['X-Workbench-Token']='test-capability'
        if body is not None:headers['Content-Type']='application/json'
        if origin:headers['Origin']=origin
        if host:headers['Host']=host
        conn.request(method,path,body=json.dumps(body) if body is not None else None,headers=headers)
        r=conn.getresponse();data=r.read();status=r.status;conn.close();return status,data
    def test_status_requires_capability(self):self.assertEqual(self.request('GET','/api/status',token=False)[0],403)
    def test_authorized_status(self):
        status,data=self.request('GET','/api/status')
        self.assertEqual(status,200);self.assertFalse(json.loads(data)['started'])
    def test_no_cross_origin_writes(self):
        self.assertEqual(self.request('POST','/api/start',{},origin='https://other.example')[0],403)
        self.assertFalse(self.w.started)
    def test_missing_origin_write_rejected(self):self.assertEqual(self.request('POST','/api/start',{})[0],403)
    def test_bad_host_rejected(self):self.assertEqual(self.request('GET','/',host='evil.example')[0],403)
    def test_arbitrary_action_rejected(self):self.assertEqual(self.request('POST','/api/execute',{'command':'calc'},origin=self.origin)[0],404)
    def test_static_source_not_exposed(self):self.assertEqual(self.request('GET','/engine.py')[0],404)
    def test_bad_options_rejected(self):self.assertEqual(self.request('POST','/api/start',{'delete_everything':True},origin=self.origin)[0],400)
    def test_run_and_report_use_simulation_marker(self):
        self.assertEqual(self.request('POST','/api/start',{'science':False,'browser':False},origin=self.origin)[0],200)
        deadline=time.monotonic()+4
        while not self.w.finished and time.monotonic()<deadline:time.sleep(.03)
        status,data=self.request('GET','/api/report')
        self.assertEqual(status,200);self.assertIn(b'"simulated": true',data)
        self.assertNotIn(b'test-capability',data)
    def test_concurrent_report_reads_remain_complete_through_final_update(self):
        self.w.write_report(final=False)
        report_path=self.w.run_dir/'Paste-Into-ChatGPT.txt'
        original_read=Path.read_bytes
        def hold_report_read(path):
            if path!=report_path:return original_read(path)
            # Keep the Windows read handle open long enough to overlap a write
            # unless the endpoint shares the Workbench report lock.
            with path.open('rb') as stream:
                content=stream.read()
                time.sleep(.02)
                return content
        def read_complete_report():
            status,content=self.request('GET','/api/report')
            self.assertEqual(status,200)
            lines=content.decode('utf-8').splitlines()
            self.assertGreaterEqual(len(lines),3,'Report must never be empty or partial')
            self.assertEqual(lines[0],'=== BEGIN OPENAI EDGE DIAGNOSTIC ===')
            self.assertEqual(lines[-1],'=== END OPENAI EDGE DIAGNOSTIC ===')
            return json.loads('\n'.join(lines[1:-1]))
        observed_intermediate=0
        with patch.object(Path,'read_bytes',hold_report_read):
            self.assertEqual(self.request('POST','/api/start',{'science':False,'browser':False},origin=self.origin)[0],200)
            deadline=time.monotonic()+10
            while time.monotonic()<deadline:
                report=read_complete_report()
                observed_intermediate+=not report['final']
                if self.w.snapshot()['finished']:break
            self.assertTrue(self.w.snapshot()['finished'],'Simulation did not finish before the deadline')
            final=read_complete_report()
        self.assertGreater(observed_intermediate,0,'Expected reads during report updates')
        self.assertTrue(final['final'])
        self.assertTrue(final['simulated'])
        self.assertNotIn('fatal_error',final)
        self.assertNotIn('report_error',self.w.report)
        self.assertEqual(len(final['results']),len(self.w.plan))
        self.assertEqual({row['status'] for row in final['results']},{'SIMULATED'})
    def test_readme_index_available(self):
        status,data=self.request('GET','/')
        self.assertEqual(status,200);self.assertIn(b'OpenAI Edge Workbench',data)
    def test_report_without_token_rejected(self):self.assertEqual(self.request('GET','/api/report',token=False)[0],403)

if __name__=='__main__':unittest.main()
