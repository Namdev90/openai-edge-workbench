"""Exercise feature authorization and jobs through the actual loopback HTTP API."""
import http.client, json, tempfile, threading, time, unittest
from pathlib import Path
from app import make_server
from engine import Workbench
from unittest.mock import patch

class FeatureApiTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.workbench=Workbench(Path(self.temp.name),simulate=True)
        self.server=make_server(self.workbench,token='fixture-token')
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.port=self.server.server_address[1];self.origin=f'http://127.0.0.1:{self.port}'
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join(2);self.temp.cleanup()
    def request(self,method,path,body=None,token=True,origin=None,host=None):
        headers={'Content-Type':'application/json'}
        if token:headers['X-Workbench-Token']='fixture-token'
        if origin:headers['Origin']=origin
        if host:headers['Host']=host
        connection=http.client.HTTPConnection('127.0.0.1',self.port,timeout=3)
        connection.request(method,path,None if body is None else json.dumps(body),headers)
        response=connection.getresponse();result=(response.status,json.loads(response.read()));connection.close();return result
    def test_catalog_history_and_jobs_require_capability_and_exact_host(self):
        for endpoint in ('/api/features','/api/features/history','/api/features/jobs/'+'a'*32):
            self.assertEqual(self.request('GET',endpoint,token=False)[0],403)
            self.assertEqual(self.request('GET',endpoint,host='evil.example')[0],403)
        status,data=self.request('GET','/api/features');self.assertEqual(status,200);self.assertEqual(len(data['features']),100)
    def test_job_requires_same_origin_and_does_not_accept_commands(self):
        body={'id':'f066','payload':{}}
        for origin in (None,'https://other.example'):
            self.assertEqual(self.request('POST','/api/features/run',body,origin=origin)[0],403)
        for invalid in ({'id':'f066','command':'calc'},{'id':'f066','payload':{'path':'../auth.json'}},{'id':'f100'}):
            self.assertEqual(self.request('POST','/api/features/run',invalid,origin=self.origin)[0],400)
        self.assertFalse(self.workbench.started)
    def test_actual_profile_job_completes_without_starting_installation(self):
        status,data=self.request('POST','/api/features/run',{'id':'f071'},origin=self.origin)
        self.assertEqual(status,202);identity=data['id'];deadline=time.monotonic()+3
        while time.monotonic()<deadline:
            status,job=self.request('GET','/api/features/jobs/'+identity)
            if job['state']!='running':break
            time.sleep(.01)
        self.assertEqual(status,200);self.assertEqual(job['state'],'complete');self.assertTrue(job['result']['simulated'])
        self.assertFalse(job['result']['options']['live']);self.assertFalse(self.workbench.started)
        self.assertEqual(self.request('GET','/api/features/jobs/../../auth.json')[0],404)

    def test_plan_requirements_and_recipe_use_explicit_dashboard_selection(self):
        # Before Start the engine still has its default options. Preview/save
        # must honor the explicit selection supplied by the dashboard instead.
        choices={name:False for name in self.workbench.options}
        choices['dotnet']=True
        outcomes={}
        for identity in ('f076','f078','f087','f088'):
            payload={'options':choices} if identity!='f088' else {}
            status,data=self.request('POST','/api/features/run',{'id':identity,'payload':payload},origin=self.origin)
            self.assertEqual(status,202)
            deadline=time.monotonic()+3
            while time.monotonic()<deadline:
                _,job=self.request('GET','/api/features/jobs/'+data['id'])
                if job['state']!='running':break
                time.sleep(.01)
            self.assertEqual(job['state'],'complete',job)
            outcomes[identity]=job['result']
        self.assertEqual(outcomes['f076']['data']['options'],choices)
        steps={row['id'] for row in outcomes['f076']['data']['steps']}
        self.assertIn('dotnet',steps)
        self.assertTrue({'science','documents','playwright','live'}.isdisjoint(steps))
        package_names={row['name'] for row in outcomes['f078']['data']['catalog_packages']}
        self.assertFalse(any('Canary' in name or 'FFmpeg' in name for name in package_names))
        self.assertFalse(outcomes['f078']['data']['model_request_selected'])
        self.assertEqual(outcomes['f088']['options'],choices)
        self.assertNotEqual(self.workbench.options,choices)
        self.assertFalse(self.workbench.started)

    def test_ai_provider_and_job_metadata_require_session_authorization(self):
        for endpoint in ('/api/ai/providers','/api/ai/jobs/'+'a'*32):
            self.assertEqual(self.request('GET',endpoint,token=False)[0],403)
            self.assertEqual(self.request('GET',endpoint,host='evil.example')[0],403)
        status,data=self.request('GET','/api/ai/providers')
        self.assertEqual(status,200);self.assertEqual({p['id'] for p in data['providers']},{'local','groq','gemini','openrouter'})
        self.assertNotIn('key',data['providers'][0]);self.assertTrue(data['providers'][0]['key_ready'])

    def test_cloud_preview_connect_and_send_reject_cross_origin_before_handling_keys(self):
        for endpoint in ('/api/ai/preview','/api/ai/connect','/api/ai/ask'):
            self.assertEqual(self.request('POST',endpoint,{'provider':'groq','key':'fixture-private-key'},origin='https://other.example')[0],403)
            self.assertEqual(self.request('POST',endpoint,{'provider':'groq'},token=False,origin=self.origin)[0],403)

    def test_zero_setup_local_guidance_works_in_simulation_through_actual_api(self):
        report={'run_id':'20261010-123456-abcdef','final':True,'finished_utc':'now','simulated':True,'results':[{'id':'node','status':'SIMULATED'}]}
        directory=Path(self.temp.name)/'reports'/report['run_id'];directory.mkdir();(directory/'Diagnostic.json').write_text(json.dumps(report))
        status,data=self.request('POST','/api/ai/ask',{'provider':'local'},origin=self.origin)
        self.assertEqual(status,202);deadline=time.monotonic()+3
        while time.monotonic()<deadline:
            status,job=self.request('GET','/api/ai/jobs/'+data['id'])
            if job['state']!='running':break
            time.sleep(.01)
        self.assertEqual(job['state'],'complete');self.assertTrue(job['result']['simulated'])
        self.assertIn('Rule-based',job['result']['limitations']);self.assertFalse(self.workbench.started)

    def test_busy_connection_returns_an_actionable_conflict_response(self):
        with patch('app.AIService.connect',side_effect=RuntimeError('One explanation is already running.')):
            status,data=self.request('POST','/api/ai/connect',{'provider':'groq','key':'synthetic-test-key'},origin=self.origin)
        self.assertEqual(status,409);self.assertIn('already running',data['error'])
