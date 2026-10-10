import base64, io, json, os, tempfile, unittest, zipfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from engine import default_options
import feature_plans as plans

class Context:
    def __init__(self,root):
        self.root=Path(root);self.workbench=SimpleNamespace(active={})
        self.report={'run_id':'20261010-123456-abcdef','simulated':True,'results':[{'id':'x','name':'<script>alert(1)</script>','status':'FAILED','detail':'=HYPERLINK("bad")'}],'checks':{}}
    def snapshot(self):return {'options':default_options()}
    def latest_report(self):return self.report
    def protect(self,value):return value
    def history(self):return [{'run_id':self.report['run_id'],'report':self.report},{'run_id':'previous','report':{'run_id':'previous','results':[]}}]
    def activity(self):return [{'feature_id':'f066','state':'complete'}]

class PlanningFeatureTests(unittest.TestCase):
    def test_profiles_are_distinct_previews_and_never_start_installation(self):
        with tempfile.TemporaryDirectory() as root:
            ctx=Context(root);seen=set()
            for feature in plans.FEATURES[:10]:
                result=plans.run(feature['id'],ctx,{})
                self.assertEqual(set(result['options']),set(default_options()))
                self.assertNotIn(tuple(result['options'].values()),seen)
                seen.add(tuple(result['options'].values()))
                self.assertIn('no installation started',result['summary'])
                self.assertEqual(list(Path(root).iterdir()),[])

    def test_options_reject_partial_strings_and_unknown_values(self):
        with tempfile.TemporaryDirectory() as root:
            ctx=Context(root)
            for values in ({}, {'browser':'yes'}, {**default_options(),'extra':True},{**default_options(),'live':1}):
                with self.subTest(values=values),self.assertRaises(ValueError):plans.run('f076',ctx,{'options':values})

    def test_saved_recipe_roundtrip_is_explicit_and_owned(self):
        with tempfile.TemporaryDirectory() as root:
            ctx=Context(root);choices={k:False for k in default_options()};choices['dotnet']=True
            plans.run('f087',ctx,{'options':choices})
            self.assertEqual(plans.run('f088',ctx,{})['options'],choices)
            plans.run('f089',ctx,{})
            with self.assertRaises(ValueError):plans.run('f088',ctx,{})
            self.assertFalse((Path(root)/'feature-workspace/selection-recipe.json').exists())

    def test_unknown_workspace_and_recipe_are_preserved(self):
        with tempfile.TemporaryDirectory() as root:
            ctx=Context(root);folder=Path(root)/'feature-workspace';folder.mkdir();file=folder/'selection-recipe.json';file.write_text('original')
            with self.assertRaises(ValueError):plans.run('f087',ctx,{})
            self.assertEqual(file.read_text(),'original')

    def test_externally_modified_matching_schema_recipe_is_preserved(self):
        with tempfile.TemporaryDirectory() as root:
            ctx=Context(root);plans.run('f087',ctx,{})
            path=Path(root)/'feature-workspace/selection-recipe.json'
            for content in ({'schema':'namu-selection-recipe/1','notes':'private added content'}, {'schema':'namu-selection-recipe/1','options':default_options(),'notes':'added'}, {'schema':'namu-selection-recipe/1','options':{}}):
                original=json.dumps(content);path.write_text(original)
                for action in ('f087','f088','f089'):
                    with self.subTest(action=action),self.assertRaises(ValueError):plans.run(action,ctx,{})
                    self.assertEqual(path.read_text(),original)

    def test_planted_legacy_temporary_files_are_never_opened_or_removed(self):
        with tempfile.TemporaryDirectory() as root:
            ctx=Context(root);folder=Path(root)/'feature-workspace';created=[]
            real_mkstemp=tempfile.mkstemp
            def plant_legacy_files(*args,**kwargs):
                for name in ('.workbench-feature-owner.json.tmp','selection-recipe.json.tmp'):
                    path=folder/name
                    if not path.exists():path.write_text('foreign temporary content')
                descriptor,name=real_mkstemp(*args,**kwargs);created.append(Path(name))
                return descriptor,name
            choices={**default_options(),'science':True}
            with patch.object(plans.tempfile,'mkstemp',side_effect=plant_legacy_files):
                plans.run('f087',ctx,{})
                plans.run('f087',ctx,{'options':choices})
            self.assertEqual(plans.run('f088',ctx,{})['options'],choices)
            self.assertEqual(len(set(created)),3)
            self.assertTrue(all(path.parent==folder and not path.exists() for path in created))
            for name in ('.workbench-feature-owner.json.tmp','selection-recipe.json.tmp'):
                self.assertEqual((folder/name).read_text(),'foreign temporary content')

    def test_planted_legacy_temp_symlink_does_not_touch_foreign_target(self):
        with tempfile.TemporaryDirectory() as root:
            ctx=Context(root);plans.run('f087',ctx,{})
            foreign=Path(root)/'private.json';foreign.write_text('private content')
            temporary=Path(root)/'feature-workspace/selection-recipe.json.tmp'
            try:temporary.symlink_to(foreign)
            except OSError as exc:self.skipTest('Symlink creation is unavailable: '+str(exc))
            plans.run('f087',ctx,{'options':{**default_options(),'science':True}})
            self.assertEqual(foreign.read_text(),'private content')
            self.assertTrue(temporary.is_symlink())

    def test_recipe_target_symlink_is_rejected_and_foreign_file_preserved(self):
        with tempfile.TemporaryDirectory() as root:
            ctx=Context(root);plans.run('f087',ctx,{})
            foreign=Path(root)/'private.json';foreign.write_text('private content')
            target=Path(root)/'feature-workspace/selection-recipe.json';target.unlink()
            try:target.symlink_to(foreign)
            except OSError as exc:self.skipTest('Symlink creation is unavailable: '+str(exc))
            for action in ('f087','f088','f089'):
                with self.subTest(action=action),self.assertRaises(ValueError):plans.run(action,ctx,{})
                self.assertEqual(foreign.read_text(),'private content')
                self.assertTrue(target.is_symlink())

    def test_atomic_recipe_replace_does_not_write_through_a_hard_link(self):
        with tempfile.TemporaryDirectory() as root:
            ctx=Context(root);plans.run('f087',ctx,{})
            target=Path(root)/'feature-workspace/selection-recipe.json'
            foreign=Path(root)/'preserved-foreign-copy.json';os.link(target,foreign)
            original=foreign.read_bytes();choices={**default_options(),'science':True}
            plans.run('f087',ctx,{'options':choices})
            self.assertEqual(foreign.read_bytes(),original)
            self.assertEqual(plans.run('f088',ctx,{})['options'],choices)

    def test_new_foreign_recipe_planted_during_temp_creation_is_preserved(self):
        with tempfile.TemporaryDirectory() as root:
            ctx=Context(root);target=plans.recipe_path(ctx,create=True)
            real_mkstemp=tempfile.mkstemp
            def plant_target(*args,**kwargs):
                result=real_mkstemp(*args,**kwargs)
                target.write_text('foreign newly created recipe')
                return result
            with patch.object(plans.tempfile,'mkstemp',side_effect=plant_target),self.assertRaises(ValueError):
                plans.run('f087',ctx,{})
            self.assertEqual(target.read_text(),'foreign newly created recipe')
            self.assertEqual(list(target.parent.glob('.workbench-recipe-*.tmp')),[])

    def test_foreign_marker_planted_at_publication_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as root:
            ctx=Context(root);folder=Path(root)/'feature-workspace';marker=folder/'.workbench-feature-owner.json'
            real_link=os.link
            def plant_marker(source,target):
                Path(target).write_text('foreign ownership marker')
                return real_link(source,target)
            with patch.object(plans.os,'link',side_effect=plant_marker),self.assertRaises(FileExistsError):
                plans.run('f087',ctx,{})
            self.assertEqual(marker.read_text(),'foreign ownership marker')
            self.assertFalse((folder/'selection-recipe.json').exists())
            self.assertEqual(list(folder.glob('.workbench-recipe-*.tmp')),[])

    def test_changed_ownership_marker_aborts_recipe_save(self):
        with tempfile.TemporaryDirectory() as root:
            ctx=Context(root);plans.run('f087',ctx,{})
            folder=Path(root)/'feature-workspace';marker=folder/'.workbench-feature-owner.json'
            target=folder/'selection-recipe.json';original=target.read_bytes()
            real_mkstemp=tempfile.mkstemp
            def replace_owner(*args,**kwargs):
                result=real_mkstemp(*args,**kwargs);marker.write_text('foreign replacement marker')
                return result
            with patch.object(plans.tempfile,'mkstemp',side_effect=replace_owner),self.assertRaises(ValueError):
                plans.run('f087',ctx,{})
            self.assertEqual(target.read_bytes(),original)
            self.assertEqual(marker.read_text(),'foreign replacement marker')
            self.assertEqual(list(folder.glob('.workbench-recipe-*.tmp')),[])

    def test_recipe_changed_after_temp_write_is_preserved(self):
        with tempfile.TemporaryDirectory() as root:
            ctx=Context(root);plans.run('f087',ctx,{})
            target=Path(root)/'feature-workspace/selection-recipe.json'
            real_fsync=os.fsync
            def replace_target(descriptor):
                real_fsync(descriptor);target.write_text('foreign replacement after temporary write')
            with patch.object(plans.os,'fsync',side_effect=replace_target),self.assertRaises(ValueError):
                plans.run('f087',ctx,{})
            self.assertEqual(target.read_text(),'foreign replacement after temporary write')
            self.assertEqual(list(target.parent.glob('.workbench-recipe-*.tmp')),[])

    def test_failed_atomic_replace_preserves_recipe_and_cleans_own_temp(self):
        with tempfile.TemporaryDirectory() as root:
            ctx=Context(root);plans.run('f087',ctx,{})
            target=Path(root)/'feature-workspace/selection-recipe.json';original=target.read_bytes()
            with patch.object(plans.os,'replace',side_effect=OSError('replacement unavailable')),self.assertRaises(OSError):
                plans.run('f087',ctx,{'options':{**default_options(),'science':True}})
            self.assertEqual(target.read_bytes(),original)
            self.assertEqual(list(target.parent.glob('.workbench-recipe-*.tmp')),[])

    def test_malformed_unknown_or_oversized_owner_marker_is_preserved(self):
        with tempfile.TemporaryDirectory() as root:
            ctx=Context(root);plans.run('f087',ctx,{})
            folder=Path(root)/'feature-workspace';marker=folder/'.workbench-feature-owner.json'
            target=folder/'selection-recipe.json';original=target.read_bytes()
            for content in ('[]','{','x'*1025,json.dumps({'owner':'namu-feature-studio-v1','schema':True}),json.dumps({**plans._RECIPE_OWNER,'notes':'foreign added content'})):
                marker.write_text(content)
                for action in ('f087','f088','f089'):
                    with self.subTest(action=action,content=content[:40]),self.assertRaises(ValueError):plans.run(action,ctx,{})
                    self.assertEqual(marker.read_text(),content)
                    self.assertEqual(target.read_bytes(),original)

    def test_nonfile_recipe_target_is_preserved(self):
        with tempfile.TemporaryDirectory() as root:
            ctx=Context(root);target=plans.recipe_path(ctx,create=True);target.mkdir()
            foreign=target/'notes.txt';foreign.write_text('foreign directory contents')
            for action in ('f087','f088','f089'):
                with self.subTest(action=action),self.assertRaises(ValueError):plans.run(action,ctx,{})
                self.assertEqual(foreign.read_text(),'foreign directory contents')

    def test_exports_identify_simulated_evidence_and_comparison_baseline(self):
        with tempfile.TemporaryDirectory() as root:
            ctx=Context(root)
            import csv
            rows=list(csv.DictReader(io.StringIO(plans.run('f083',ctx,{})['download']['text'])))
            self.assertEqual(rows[0]['report_simulated'],'True')
            self.assertEqual(rows[0]['report_final'],'False')
            comparison=json.loads(plans.run('f086',ctx,{})['download']['text'])
            self.assertTrue(comparison['to_simulated']);self.assertFalse(comparison['from_simulated'])
            self.assertFalse(comparison['from_final'])

    def test_html_escapes_untrusted_report_markup_and_csv_blocks_formulas(self):
        with tempfile.TemporaryDirectory() as root:
            ctx=Context(root)
            result=plans.run('f084',ctx,{})['download']['text']
            self.assertNotIn('<script>',result);self.assertIn('&lt;script&gt;',result)
            self.assertIn("'=HYPERLINK",plans.run('f083',ctx,{})['download']['text'])

    def test_bundle_contains_only_report_summary_and_matching_checksums(self):
        with tempfile.TemporaryDirectory() as root:
            ctx=Context(root);item=plans.run('f085',ctx,{})['download']
            with zipfile.ZipFile(io.BytesIO(base64.b64decode(item['text']))) as bundle:
                self.assertEqual(set(bundle.namelist()),{'Diagnostic.json','Review.md','SHA256SUMS.txt'})
                self.assertTrue(json.loads(bundle.read('Diagnostic.json'))['simulated'])
                import hashlib
                for line in bundle.read('SHA256SUMS.txt').decode().splitlines():
                    digest,name=line.split('  ');self.assertEqual(hashlib.sha256(bundle.read(name)).hexdigest(),digest)

    def test_every_plan_and_export_has_a_working_handler(self):
        with tempfile.TemporaryDirectory() as root:
            ctx=Context(root)
            for feature in plans.FEATURES:
                with self.subTest(feature=feature['id']):
                    result=plans.run(feature['id'],ctx,{})
                    self.assertIsInstance(result['summary'],str)
                    self.assertIn('data',result)
