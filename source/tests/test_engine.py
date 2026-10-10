import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
import engine

class PolicyTests(unittest.TestCase):
    def test_alpha_numeric_not_lexical(self):
        self.assertGreater(engine.semver_key('0.163.0-alpha.20'), engine.semver_key('0.163.0-alpha.9'))
    def test_stable_beats_same_version_prerelease(self):
        self.assertGreater(engine.semver_key('1.2.0'), engine.semver_key('1.2.0-rc.9'))
    def test_future_alpha_beats_old_stable(self):
        self.assertEqual(engine.choose_npm({'versions': {'1.0.0': {}, '1.1.0-alpha.4': {}}}), '1.1.0-alpha.4')
    def test_superseded_preview_not_selected(self):
        self.assertEqual(engine.choose_npm({'versions': {'1.1.0': {}, '1.1.0-alpha.4': {}}}), '1.1.0')
    def test_deprecated_and_platform_package_versions_not_selected(self):
        self.assertEqual(engine.choose_npm({'versions': {'2.0.0-linux-x64': {}, '1.1.0-alpha.4': {'deprecated': 'bad'}, '1.0.0': {}}}), '1.0.0')
    def test_no_made_up_tag(self):
        with self.assertRaises(ValueError): engine.choose_npm({'versions': {}})
    def test_python_prereleases(self):
        self.assertGreater(engine.python_key('3.16.0a1'), engine.python_key('3.15.0'))
        self.assertGreater(engine.python_key('3.15.0rc2'), engine.python_key('3.15.0b5'))
        self.assertGreater(engine.python_key('3.15.0'), engine.python_key('3.15.0rc2'))
    def test_uv_filter_implementation_variant_and_architecture(self):
        data=[{'key':'cpython-3.15.0rc2-windows-x86_64-none', 'version':'3.15.0rc2'},
              {'key':'cpython-3.16.0a1+freethreaded-windows-x86_64-none', 'version':'3.16.0a1'},
              {'key':'cpython-3.16.0a1-windows-aarch64-none', 'version':'3.16.0a1'},
              {'key':'pypy-3.99.0-windows-x86_64-none', 'version':'3.99.0'}]
        self.assertEqual(engine.choose_python(data,'x64')['version'],'3.15.0rc2')
    def test_secret_redaction(self):
        raw='key sk-proj-'+'a'*30+' token ghp_'+'b'*40+' Bearer aaa.bbb.ccc user a@b.com https://example.org/path?token=SECRET'
        s=engine.redact(raw)
        for forbidden in ['sk-proj-','ghp_','aaa.bbb.ccc','a@b.com','SECRET']:
            self.assertNotIn(forbidden,s)
    def test_settings_secret_assignments(self):
        s=engine.redact('"access_token": "secretvalue"\npassword=private123\nAuthorization: bearer abcd')
        self.assertNotIn('secretvalue',s); self.assertNotIn('private123',s);self.assertNotIn('abcd',s)
    def test_trusted_download_url(self):
        self.assertTrue(engine.trusted_url('https://nodejs.org/download/nightly/index.json'))
        self.assertFalse(engine.trusted_url('http://nodejs.org/download/nightly/index.json'))
        self.assertFalse(engine.trusted_url('https://nodejs.org.evil.test/file.zip'))
        self.assertFalse(engine.trusted_url('https://x:secret@nodejs.org/a'))
    def test_zip_traversal(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t); z=p/'bad.zip'
            with zipfile.ZipFile(z,'w') as f:f.writestr('../outside','bad')
            with self.assertRaises(ValueError):engine.safe_extract(z,p/'out')
            self.assertFalse((p/'outside').exists())
    def test_zip_windows_path_traversal(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);z=p/'bad.zip'
            with zipfile.ZipFile(z,'w') as f:f.writestr('C:/evil.exe','bad')
            with self.assertRaises(ValueError):engine.safe_extract(z,p/'out')
    def test_zip_safe_extract(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);z=p/'ok.zip'
            with zipfile.ZipFile(z,'w') as f:f.writestr('package/tool.exe','ok')
            engine.safe_extract(z,p/'out')
            self.assertEqual((p/'out/package/tool.exe').read_text(),'ok')
    def test_merge_keeps_target_and_tracks_conflict(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);a=p/'a';b=p/'b';a.mkdir();b.mkdir()
            (a/'settings.json').write_text('old');(b/'settings.json').write_text('new')
            (a/'keybindings.json').write_text('copy')
            result=engine.merge_missing(a,b)
            self.assertEqual((b/'settings.json').read_text(),'new')
            self.assertEqual((b/'keybindings.json').read_text(),'copy')
            self.assertIn('settings.json',result['conflicts'])
    def test_merge_does_not_copy_auth_and_storage(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);a=p/'a';b=p/'b';a.mkdir()
            (a/'globalStorage').mkdir();(a/'globalStorage'/'state.vscdb').write_text('secret')
            (a/'auth.json').write_text('secret')
            engine.merge_missing(a,b)
            self.assertFalse((b/'globalStorage').exists());self.assertFalse((b/'auth.json').exists())
    def test_plan_includes_required_and_not_heavy_by_default(self):
        keys=[x['id'] for x in engine.build_plan(engine.default_options())]
        for key in ['chatgpt','node','codex','python','python-packages','migrate','verify','report']:self.assertIn(key,keys)
        self.assertNotIn('docker',keys);self.assertNotIn('wsl',keys)
    def test_duplicate_plan_ids(self):
        items=engine.build_plan(engine.default_options());self.assertEqual(len(items),len({x['id'] for x in items}))
    def test_false_install_success_not_verified(self):
        self.assertFalse(engine.version_matches('','1.2.3'))
        self.assertFalse(engine.version_matches('tool 1.2.30','1.2.3'))
        self.assertTrue(engine.version_matches('codex-cli 1.2.3-alpha.4','1.2.3-alpha.4'))
    def test_current_app_is_not_classic(self):
        items=engine.build_plan(engine.default_options())
        current=next(x for x in items if x['id']=='chatgpt')
        self.assertEqual(current['package'],'9PLM9XGG6VKS')
        self.assertNotEqual(current['package'],'9NT1R1C2HH7J')

if __name__=='__main__':unittest.main()
