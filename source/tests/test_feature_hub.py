import json, tempfile, time, unittest
from pathlib import Path
from unittest.mock import patch
from engine import Workbench
from feature_hub import FeatureService, FeatureContext, FEATURES, protect

class FeatureHubTests(unittest.TestCase):
    def test_exact_catalog_is_one_hundred_distinct_usable_capabilities(self):
        self.assertEqual(len(FEATURES),100)
        self.assertEqual({x['id'] for x in FEATURES},{f'f{i:03}' for i in range(1,101)})
        self.assertTrue(all(x['description'] and x['effect'] for x in FEATURES))

    def test_invalid_inputs_and_client_controls_cannot_be_server_commands(self):
        with tempfile.TemporaryDirectory() as root:
            service=FeatureService(Workbench(Path(root),simulate=True))
            for feature,payload in [('unknown',{}),('f091',{}),('f066',{'command':'evil'}),('f066',{'path':'../../auth.json'}),('f066',{'run_id':1})]:
                with self.subTest(feature=feature,payload=payload),self.assertRaises(ValueError):service.start(feature,payload)

    def test_async_profile_result_keeps_simulation_and_does_not_start_worker(self):
        with tempfile.TemporaryDirectory() as root:
            workbench=Workbench(Path(root),simulate=True);service=FeatureService(workbench)
            identity=service.start('f066',{})['id'];deadline=time.monotonic()+5
            while service.get(identity)['state']=='running' and time.monotonic()<deadline:time.sleep(.02)
            result=service.get(identity)
            self.assertEqual(result['state'],'complete');self.assertTrue(result['result']['simulated'])
            self.assertFalse(workbench.started)

    def test_history_excludes_partial_invalid_and_unfinished_reports(self):
        with tempfile.TemporaryDirectory() as root:
            service=FeatureService(Workbench(Path(root),simulate=True));folder=Path(root)/'reports';folder.mkdir(exist_ok=True)
            for i,valid in enumerate((True,False)):
                run=f'20261010-12345{i}-abcdef';directory=folder/run;directory.mkdir()
                (directory/'Diagnostic.json').write_text(json.dumps({'run_id':run,'final':valid,'finished_utc':'2026-10-10T12:00:00Z','results':[]}))
            self.assertEqual(len(service.history()['reports']),1)
            with self.assertRaises(ValueError):FeatureContext(service,{'run_id':'../../other'}).latest_report()

    def test_recipes_cannot_be_changed_during_installation(self):
        with tempfile.TemporaryDirectory() as root:
            workbench=Workbench(Path(root),simulate=True);workbench.started=True
            service=FeatureService(workbench)
            for feature in ('f087','f089'):
                with self.assertRaises(RuntimeError):service.start(feature,{})

    def test_disabled_diagnostic_cannot_contact_network_or_execute_commands_in_simulation(self):
        with tempfile.TemporaryDirectory() as root:
            ctx=FeatureContext(FeatureService(Workbench(Path(root),simulate=True)),{})
            with patch('subprocess.run',side_effect=AssertionError('No real command')):
                self.assertTrue(ctx.command(['definitely-not-installed'])['simulated'])
            with self.assertRaises(ValueError):ctx.fetch_json('https://nodejs.org/download/nightly/index.json')

    def test_report_secret_keys_are_redacted_without_corrupting_json(self):
        value={'checks':{'password':'ordinary secret','api_key':'unpatterned key','authorization':['private']},'detail':'kept','download':{'encoding':'base64','text':'UEsDBA=='}}
        result=protect(value)
        self.assertEqual(result['checks'],dict.fromkeys(value['checks'],'[REDACTED]'))
        self.assertEqual(json.loads(json.dumps(result))['download']['text'],'UEsDBA==')
        self.assertEqual(value['checks']['password'],'ordinary secret')

    def test_malformed_report_results_are_excluded_from_history(self):
        with tempfile.TemporaryDirectory() as root:
            service=FeatureService(Workbench(Path(root),simulate=True));folder=Path(root)/'reports'/'20261010-123456-abcdef';folder.mkdir()
            (folder/'Diagnostic.json').write_text(json.dumps({'run_id':folder.name,'final':True,'finished_utc':'now','results':42}))
            self.assertEqual(service.history()['reports'],[])

    def test_bounded_job_admission_does_not_start_a_third_operation(self):
        import threading
        with tempfile.TemporaryDirectory() as root:
            service=FeatureService(Workbench(Path(root),simulate=True));gate=threading.Event()
            def blocked(*args):gate.wait(3);return {'summary':'fixture','data':{}}
            with patch('feature_plans.run',side_effect=blocked):
                ids=[service.start('f066',{})['id'] for _ in range(2)]
                try:
                    with self.assertRaises(RuntimeError):service.start('f066',{})
                finally:gate.set()
                deadline=time.monotonic()+4
                while any(service.get(identity)['state']=='running' for identity in ids) and time.monotonic()<deadline:time.sleep(.01)
                self.assertTrue(all(service.get(identity)['state']=='complete' for identity in ids))

    def test_catalog_rejects_foreign_hosts_ports_and_credentials_before_network(self):
        with tempfile.TemporaryDirectory() as root:
            ctx=FeatureContext(FeatureService(Workbench(Path(root),simulate=False)),{})
            with patch('urllib.request.build_opener',side_effect=AssertionError('No network')):
                for url in ('http://nodejs.org/index.json','https://evil.example/index.json','https://nodejs.org:8443/index.json','https://user:secret@nodejs.org/index.json'):
                    with self.subTest(url=url),self.assertRaises(ValueError):ctx.fetch_json(url)

    def test_sanitized_json_export_survives_service_without_second_lexical_redaction(self):
        with tempfile.TemporaryDirectory() as root:
            workbench=Workbench(Path(root),simulate=True);service=FeatureService(workbench)
            report={'run_id':'20261010-123456-abcdef','final':True,'finished_utc':'now','results':[],'checks':{'password':'opaque-secret','api_key':'another-secret'}}
            directory=Path(root)/'reports'/report['run_id'];directory.mkdir();(directory/'Diagnostic.json').write_text(json.dumps(report))
            identity=service.start('f081',{})['id'];deadline=time.monotonic()+3
            while service.get(identity)['state']=='running' and time.monotonic()<deadline:time.sleep(.01)
            job=service.get(identity);self.assertEqual(job['state'],'complete')
            exported=json.loads(job['result']['download']['text'])
            self.assertEqual(exported['checks'],{'password':'[REDACTED]','api_key':'[REDACTED]'})
