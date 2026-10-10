import unittest,json,hashlib,zipfile,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parents[1]
class Distribution(unittest.TestCase):
 def test_engine_exists(self):self.assertTrue((ROOT/'Edge.ps1').is_file())
 def test_catalog_exists(self):self.assertTrue((ROOT/'catalog.json').is_file())
 def test_bootstrap_exists(self):self.assertTrue((ROOT/'install.ps1').is_file())
 def test_catalog_ids_unique(self):
  c=json.loads((ROOT/'catalog.json').read_text());ids=[p['id'] for p in c['packages']];self.assertEqual(len(ids),len(set(ids)))
 def test_official_chatgpt(self):
  p=json.loads((ROOT/'catalog.json').read_text())['packages'][0];self.assertEqual((p['id'],p['source']),('9PLM9XGG6VKS','msstore'))
 def test_no_blanket_upgrades_or_security_bypasses(self):
  s=(ROOT/'Edge.ps1').read_text().lower()
  for bad in ['--ignore-security-hash','--disable-certificate','danger-full-access','winget upgrade --all','set-executionpolicy','auth.json']:self.assertNotIn(bad,s)
 def test_no_communication_automation(self):
  s=(ROOT/'Edge.ps1').read_text().lower()
  for bad in ['send-mailmessage','gh issue create','git push','invoke-expression']:self.assertNotIn(bad,s)
 def test_worker_and_gui_are_separate(self):
  s=(ROOT/'Edge.ps1').read_text();self.assertIn('-Worker -Root ',s);self.assertIn('Windows.Forms.Timer',s);self.assertIn('events.jsonl',s)
 def test_self_update_commit_and_integrity_checks(self):
  s=(ROOT/'install.ps1').read_text();self.assertIn('/$sha/$prefix',s);self.assertIn('Get-FileHash $target -Algorithm SHA256',s);self.assertIn('Test-Build $stage',s)
 def test_weekly_and_readback(self):
  s=(ROOT/'Edge.ps1').read_text();self.assertIn('-Weekly -WeeksInterval 1',s);self.assertIn('Get-ScheduledTaskInfo',s);self.assertIn('-LogonType Interactive -RunLevel Limited',s)
 def test_no_readonly_variable_assignments(self):
  self.assertIsNone(re.search(r'(?i)\$(?:home|pid|host)\s*=',(ROOT/'Edge.ps1').read_text()))
 def test_no_scrubbing_serialized_json(self):
  self.assertNotIn('$json=Protect-Text ($report|ConvertTo-Json',(ROOT/'Edge.ps1').read_text())
 def test_source_integrity(self):
  if not (ROOT/'release.json').exists():self.skipTest('unpublished source tree')
  m=json.loads((ROOT/'release.json').read_text());self.assertEqual(m['schema'],2)
  for n,h in m['files'].items():
   self.assertFalse(n.startswith('/') or '..' in pathlib.PurePosixPath(n).parts)
   self.assertEqual(hashlib.sha256((ROOT/n).read_bytes()).hexdigest(),h,n)
if __name__=='__main__':unittest.main()
