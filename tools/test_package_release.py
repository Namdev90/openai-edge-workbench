"""Offline regressions for release staging and preservation of local files."""
import hashlib
from pathlib import Path
import subprocess
import stat
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import package_release as package


class ReleasePackageTests(unittest.TestCase):
    def test_real_payload_stages_exact_reproducible_assets_and_checksums(self):
        with tempfile.TemporaryDirectory() as temporary:
            first, second = Path(temporary) / 'first', Path(temporary) / 'second'
            version = package.stage_release(first)
            self.assertEqual(package.stage_release(second), version)
            expected = set(package.COPY_NAMES) | {package.SOURCE_NAME, package.CHECKSUM_NAME}
            self.assertEqual({p.name for p in first.iterdir()}, expected)
            self.assertEqual({p.name for p in second.iterdir()}, expected)
            for name in expected:
                self.assertEqual((first / name).read_bytes(), (second / name).read_bytes())
            sums = (first / package.CHECKSUM_NAME).read_text().splitlines()
            self.assertEqual(len(sums), 6)
            for line in sums:
                digest, name = line.split('  ')
                self.assertEqual(hashlib.sha256((first / name).read_bytes()).hexdigest(), digest)

    def test_existing_output_directory_and_foreign_files_are_preserved(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'release'
            output.mkdir()
            sentinel = output / 'Setup.ps1'
            sentinel.write_bytes(b'unrelated existing file')
            with patch.object(package.subprocess, 'run') as verify:
                with self.assertRaisesRegex(FileExistsError, 'already exists'):
                    package.stage_release(output)
                verify.assert_not_called()
            self.assertEqual(sentinel.read_bytes(), b'unrelated existing file')
            self.assertEqual(list(output.iterdir()), [sentinel])

    def test_existing_empty_directory_and_file_are_also_preserved(self):
        with tempfile.TemporaryDirectory() as temporary:
            for kind in ('directory', 'file'):
                output = Path(temporary) / kind
                output.mkdir() if kind == 'directory' else output.write_bytes(b'original')
                with self.subTest(kind=kind), self.assertRaises(FileExistsError):
                    package.stage_release(output)
                self.assertTrue(output.is_dir() if kind == 'directory' else output.read_bytes() == b'original')

    def test_missing_parent_does_not_create_partial_directories(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'missing' / 'release'
            with self.assertRaisesRegex(ValueError, 'parent directory'):
                package.stage_release(output)
            self.assertFalse(output.parent.exists())

    def test_output_symlink_dangling_symlink_and_parent_symlink_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / 'target'; target.mkdir()
            link = root / 'link'
            try:
                link.symlink_to(target, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest('Symlinks unavailable for this test account.')
            dangling = root / 'dangling'; dangling.symlink_to(root / 'absent', target_is_directory=True)
            for output in (link, link / 'release', dangling):
                with self.subTest(output=output), self.assertRaisesRegex(ValueError, 'symlink or junction'):
                    package.stage_release(output)
            self.assertEqual(list(target.iterdir()), [])
            self.assertTrue(link.is_symlink()); self.assertTrue(dangling.is_symlink())

    def test_failed_verification_creates_no_output_and_uses_isolated_python(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'release'
            with patch.object(package.subprocess, 'run', side_effect=subprocess.CalledProcessError(1, 'verify')) as verify:
                with self.assertRaises(subprocess.CalledProcessError):
                    package.stage_release(output)
            self.assertIn('-I', verify.call_args.args[0])
            self.assertFalse(output.exists())

    def test_windows_reparse_point_is_rejected_without_path_is_junction(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'release'
            original = Path.lstat
            def reparse(path):
                if path == output:
                    return SimpleNamespace(st_mode=stat.S_IFDIR, st_file_attributes=0x400)
                return original(path)
            with patch.object(Path, 'lstat', reparse), self.assertRaisesRegex(ValueError, 'junction'):
                package.stage_release(output)
            self.assertFalse(output.exists())

    def test_concurrent_artifact_is_not_replaced_and_partial_output_cannot_be_reused(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'release'
            original = Path.open
            def competing_file(path, mode='r', *args, **kwargs):
                if path == output / 'Run.ps1' and mode == 'xb':
                    with original(path, 'wb') as stream:
                        stream.write(b'foreign file')
                return original(path, mode, *args, **kwargs)
            with patch.object(Path, 'open', competing_file), self.assertRaises(FileExistsError):
                package.stage_release(output)
            self.assertEqual((output / 'Run.ps1').read_bytes(), b'foreign file')
            self.assertFalse((output / package.CHECKSUM_NAME).exists())
            with self.assertRaises(FileExistsError):
                package.stage_release(output)

    def test_cli_failure_is_nonzero_and_does_not_claim_success(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = subprocess.run([sys.executable, str(package.ROOT / 'tools/package_release.py'),
                                     '--output', temporary], text=True, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('already exists', result.stderr)
            self.assertNotIn('Staged seven', result.stdout)
            self.assertNotIn('Traceback', result.stderr)

    def test_destination_created_during_verification_is_preserved(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'release'
            def competing_output(*args, **kwargs):
                output.mkdir(); (output / 'foreign.txt').write_bytes(b'preserve')
            with patch.object(package.subprocess, 'run', side_effect=competing_output):
                with self.assertRaises(FileExistsError):
                    package.stage_release(output)
            self.assertEqual((output / 'foreign.txt').read_bytes(), b'preserve')
            self.assertEqual(len(list(output.iterdir())), 1)

    def test_destination_created_between_final_check_and_mkdir_is_preserved(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'release'
            original = Path.mkdir

            def competing_directory(path, *args, **kwargs):
                if path == output:
                    original(path)
                    (path / 'foreign.txt').write_bytes(b'preserve')
                return original(path, *args, **kwargs)

            with patch.object(Path, 'mkdir', competing_directory), self.assertRaises(FileExistsError):
                package.stage_release(output)
            self.assertEqual((output / 'foreign.txt').read_bytes(), b'preserve')
            self.assertEqual(len(list(output.iterdir())), 1)

    def test_failed_write_leaves_partial_output_without_success_checksum(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'release'
            original = Path.open

            def failed_write(path, mode='r', *args, **kwargs):
                if path == output / 'Run.ps1' and mode == 'xb':
                    raise OSError('simulated disk failure')
                return original(path, mode, *args, **kwargs)

            with patch.object(Path, 'open', failed_write):
                with self.assertRaisesRegex(OSError, 'simulated disk failure'):
                    package.stage_release(output)
            self.assertTrue((output / 'Setup.ps1').is_file())
            self.assertFalse((output / package.CHECKSUM_NAME).exists())
            with self.assertRaises(FileExistsError):
                package.stage_release(output)

    def test_changed_input_after_verification_fails_before_output_creation(self):
        with tempfile.TemporaryDirectory() as temporary:
            original = Path.read_bytes
            def changed_bytes(path):
                content = original(path)
                return content + b'changed' if path == package.ROOT / 'Setup.ps1' else content
            output = Path(temporary) / 'release'
            with patch.object(package.subprocess, 'run'), patch.object(Path, 'read_bytes', changed_bytes):
                with self.assertRaisesRegex(ValueError, 'changed after verification'):
                    package.stage_release(output)
            self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()
