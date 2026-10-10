"""Offline boundary regressions for the isolated reference/stat experiment."""
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import build_language_lab as lab


class LanguageLabTests(unittest.TestCase):
    def setUp(self):self.catalog=lab.load_catalog()

    def test_snapshot_coverage_and_generation_are_deterministic_and_offline(self):
        with patch('urllib.request.urlopen',side_effect=AssertionError('No network during normal generation.')):
            first,files=lab.generated_files(self.catalog)
            second,repeated=lab.generated_files(self.catalog)
        self.assertEqual(first,second);self.assertEqual(files,repeated)
        self.assertEqual(first['counts']['entries'],836)
        self.assertEqual(first['counts']['statistical_groups'],754)
        self.assertEqual(len(files),838)
        for row in first['languages']:
            content=files[row['fixture']]
            self.assertEqual(len(content),row['fixture_bytes'])
            self.assertLessEqual(len(content),lab.FIXTURE_LIMIT)
            self.assertIn(b'Program validity: not claimed.',content)
            self.assertIn(row['name'].encode(),content)
            self.assertIn(row['upstream_url'].encode(),content)

    def test_path_attribute_and_provenance_injection_are_rejected(self):
        changes=[('fixture','../../Setup.ps1'),('override_alias','Python\nsource/** linguist-language=C'),
                 ('upstream_url','https://untrusted.example/metadata'),('aliases',['private\ncontrol'])]
        for field,value in changes:
            catalog=copy.deepcopy(self.catalog);catalog['languages'][0][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):lab.generated_files(catalog)

    def test_malformed_lists_types_counts_and_unknown_fields_are_rejected(self):
        changes=[('aliases',[{}]),('type',[]),('color',42),('fixture_bytes',True)]
        for field,value in changes:
            catalog=copy.deepcopy(self.catalog);catalog['languages'][0][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):lab.validate_catalog(catalog)
        catalog=copy.deepcopy(self.catalog);catalog['counts']['entries']=836.0
        with self.assertRaises(ValueError):lab.validate_catalog(catalog)
        catalog=copy.deepcopy(self.catalog);catalog['extra']='unknown data'
        with self.assertRaises(ValueError):lab.validate_catalog(catalog)

    def test_duplicate_identifiers_and_wrong_group_parent_are_rejected(self):
        catalog=copy.deepcopy(self.catalog);catalog['languages'][1]['language_id']=catalog['languages'][0]['language_id']
        catalog['languages'][1]['fixture']=catalog['languages'][0]['fixture']
        with self.assertRaises(ValueError):lab.validate_catalog(catalog)
        catalog=copy.deepcopy(self.catalog);catalog['languages'][0]['group']='Unknown parent'
        with self.assertRaises(ValueError):lab.validate_catalog(catalog)

    def test_attributes_use_exact_numeric_files_and_exclude_generated_presentation(self):
        attributes=lab.attribute_text(self.catalog)
        fixture_lines=[line for line in attributes.splitlines() if line.startswith('fixtures/')]
        self.assertEqual(len(fixture_lines),836)
        for line in fixture_lines:
            path=line.split()[0]
            self.assertRegex(path,r'^fixtures/lang-\d+\.fixture$')
            self.assertIn('linguist-detectable=true',line)
            self.assertIn('linguist-generated=false',line)
        self.assertIn('index.html linguist-generated=true\n',attributes)
        self.assertIn('README.md linguist-generated=true linguist-documentation=true\n',attributes)
        self.assertNotIn('source/',attributes)

    def test_foreign_existing_output_is_preserved(self):
        with tempfile.TemporaryDirectory() as temporary:
            for name in ('lang-0.fixture','.gitattributes'):
                target=Path(temporary)/name;target.write_bytes(b'foreign content')
                with self.subTest(name=name),self.assertRaises(ValueError):lab.atomic_output(target,b'replacement')
                self.assertEqual(target.read_bytes(),b'foreign content')

    def test_failed_replacement_preserves_reference_and_cleans_unique_temp(self):
        with tempfile.TemporaryDirectory() as temporary:
            target=Path(temporary)/'lang-0.fixture';original=lab.REFERENCE_SIGNATURE.encode()+b'original'
            target.write_bytes(original)
            planted=Path(temporary)/'lang-0.fixture.tmp';planted.write_bytes(b'foreign temp')
            with patch.object(lab.os,'replace',side_effect=OSError('failed')),self.assertRaises(OSError):
                lab.atomic_output(target,lab.REFERENCE_SIGNATURE.encode()+b'updated')
            self.assertEqual(target.read_bytes(),original)
            self.assertEqual(planted.read_bytes(),b'foreign temp')
            self.assertEqual(list(Path(temporary).glob('.language-lab-*.tmp')),[])


if __name__=='__main__':unittest.main()
