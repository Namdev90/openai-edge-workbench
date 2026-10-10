import json
import unittest
import engine

class DoctorReportingTests(unittest.TestCase):
    def test_warning_details_survive_long_success_lists(self):
        rows={str(i):{'status':'ok','summary':'healthy'} for i in range(50)}
        rows['mcp']={'status':'warning','summary':'Missing optional MCP environment','details':{'21st':'API_KEY_21ST missing'},'remediation':'Configure the required environment'}
        rows['history']={'status':'warning','summary':'History paths differ','details':{'missing rows':'34'}}
        result=engine.summarize_codex_doctor(json.dumps({'overallStatus':'warning','checks':rows}))
        self.assertEqual(result['warning_count'],2)
        self.assertEqual(result['counts']['ok'],50)
        self.assertEqual(result['non_ok_checks'][0]['details']['21st'],'API_KEY_21ST missing')
        self.assertEqual(result['non_ok_checks'][1]['id'],'history')

    def test_failed_check_not_hidden_by_successful_process(self):
        result=engine.summarize_codex_doctor(json.dumps({'overallStatus':'error','checks':{'x':{'status':'error','summary':'Broken'}}}))
        self.assertEqual(result['failure_count'],1)
        self.assertEqual(result['overall_status'],'error')

    def test_credentials_in_unexpected_details_are_redacted(self):
        result=engine.summarize_codex_doctor(json.dumps({'checks':{'x':{'status':'warning','details':{'credential':'Bearer abcdefghijklmnopqrstuvwxyz1234567890'}}}}))
        self.assertNotIn('abcdefghijklmnopqrstuvwxyz1234567890',json.dumps(result))

    def test_malformed_output_remains_unverified(self):
        for text in ('not JSON','[]','{}','{"checks":{"x":{"status":null}}}'):
            with self.subTest(text=text), self.assertRaises(engine.OperationError):engine.summarize_codex_doctor(text)
