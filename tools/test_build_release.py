"""Cross-platform release byte and ZIP metadata regressions, without modifying the checkout."""
import base64
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ('OpenAI-Edge-Workbench.cmd', 'OpenAI-Edge-Workbench-Setup.cmd', 'release.json')


class ReleaseBuildTests(unittest.TestCase):
    def prepare(self, root, real_source=False):
        (root / 'tools').mkdir()
        for name in ('build_release.py', 'launcher-loader.ps1', 'first-stage.ps1'):
            shutil.copyfile(ROOT / 'tools' / name, root / 'tools' / name)
        shutil.copyfile(ROOT / 'Setup.ps1', root / 'Setup.ps1')
        if real_source:
            shutil.copytree(ROOT / 'source', root / 'source', ignore=shutil.ignore_patterns('__pycache__'))
        else:
            (root / 'source').mkdir()
            (root / 'source' / 'engine.py').write_bytes(b"VERSION = '0.0.0-test'\n")

    def build(self, root):
        subprocess.run([sys.executable, '-I', str(root / 'tools/build_release.py')],
                       check=True, capture_output=True, text=True)
        return {name: (root / name).read_bytes() for name in ARTIFACTS}

    def test_real_source_rebuild_matches_checked_in_assets_twice(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.prepare(root, real_source=True)
            expected = {name: (ROOT / name).read_bytes() for name in ARTIFACTS}
            first = self.build(root)
            second = self.build(root)
            for name in ARTIFACTS:
                with self.subTest(artifact=name):
                    self.assertTrue(first[name] == expected[name],
                                    name + ' differs from the checked-in release; rebuild intentionally if source changed')
                    self.assertTrue(first[name] == second[name], name + ' changed on a repeated build')

    def test_mixed_case_paths_use_fixed_component_order_and_zip_metadata(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.prepare(root)
            # Creation order deliberately differs from archive order. Component
            # sorting also puts a directory before a similarly prefixed file.
            for name in ('z.py', 'README.md', 'a.py', 'A/Two.py', 'A/one.py'):
                path = root / 'source' / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b'# fixture\n')
            artifacts = self.build(root)
            marker = b'\r\n::EDGE_PAYLOAD\r\n'
            payload = base64.b64decode(b''.join(artifacts[ARTIFACTS[0]].split(marker)[1].split()))
            expected = ['A/one.py', 'A/Two.py', 'a.py', 'engine.py', 'README.md', 'z.py']
            with zipfile.ZipFile(io.BytesIO(payload)) as archive:
                self.assertEqual(archive.namelist(), expected)
                for entry in archive.infolist():
                    with self.subTest(entry=entry.filename):
                        self.assertEqual(entry.create_system, 0)
                        self.assertEqual(entry.external_attr, 0o600 << 16)
                        self.assertEqual(entry.date_time, (2026, 10, 10, 0, 0, 0))
                        self.assertEqual(entry.compress_type, zipfile.ZIP_DEFLATED)
                        self.assertEqual(archive.read(entry), (root / 'source' / entry.filename).read_bytes())
            manifest = json.loads(artifacts['release.json'])
            self.assertEqual(list(manifest['sourceFiles']), expected)


if __name__ == '__main__':
    unittest.main()
