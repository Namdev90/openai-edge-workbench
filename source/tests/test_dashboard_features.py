"""Dashboard contracts that preserve setup behavior and the protected feature UI."""
from html.parser import HTMLParser
import json
from pathlib import Path
import shutil
import subprocess
import unittest

from engine import default_options


class AssetParser(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.elements = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))


class DashboardFeatureContracts(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).resolve().parents[1]
        self.html = (root / 'index.html').read_text(encoding='utf-8-sig')
        self.js = (root / 'app.js').read_text(encoding='utf-8-sig')
        self.assets = AssetParser(self.html)
        self.ids = {attrs['id']: (tag, attrs) for tag, attrs in self.assets.elements if 'id' in attrs}

    def test_existing_installer_controls_and_all_options_remain_available(self):
        required = {'start', 'pause', 'countdown', 'quit', 'stop', 'banner', 'results',
                    'progress', 'copy', 'download', 'reports', 'terminal', 'reportFallback', 'follow', 'log'}
        self.assertTrue(required <= self.ids.keys())
        actual = {attrs['name'] for tag, attrs in self.assets.elements
                  if tag == 'input' and attrs.get('type') == 'checkbox' and 'name' in attrs}
        self.assertEqual(actual, set(default_options()))
        self.assertIn('name="dotnet">', self.html, 'The launcher selects .NET by replacing this safe literal.')
        self.assertIn('Automatic start in 12 seconds', self.html)

    def test_ids_and_accessibility_references_are_valid(self):
        ids = [attrs['id'] for _, attrs in self.assets.elements if 'id' in attrs]
        self.assertEqual(len(ids), len(set(ids)), 'Duplicate IDs break labels and keyboard controls.')
        for tag, attrs in self.assets.elements:
            if tag == 'label' and 'for' in attrs:
                self.assertIn(attrs['for'], self.ids)
            for reference in attrs.get('aria-labelledby', '').split():
                self.assertIn(reference, self.ids)
        self.assertIn('main', self.ids)
        self.assertTrue(any(tag == 'nav' and attrs.get('aria-label') for tag, attrs in self.assets.elements))

    def test_assets_remain_compatible_with_strict_content_security_policy(self):
        for tag, attrs in self.assets.elements:
            self.assertFalse(any(name.lower().startswith('on') for name in attrs), 'Inline event handlers violate CSP.')
            self.assertNotIn('style', attrs, 'Styles belong in the external stylesheet.')
            if tag == 'script':
                self.assertEqual(attrs.get('src'), '/app.js')
            if 'href' in attrs:
                self.assertFalse(attrs['href'].lower().startswith('javascript:'))
        self.assertNotIn('innerHTML', self.js)
        self.assertNotIn('insertAdjacentHTML', self.js)

    def test_all_ten_client_capabilities_have_real_controls(self):
        controls = {'featureSearch', 'featureCategory', 'featureGrid', 'favoritesOnly',
                    'featureDensity', 'fontScale', 'reduceMotion', 'logSearch', 'logSeverity', 'commandPalette'}
        self.assertTrue(controls <= self.ids.keys())
        self.assertEqual(self.ids['featureSearch'][1]['type'], 'search')
        self.assertEqual(self.ids['fontScale'][1]['type'], 'range')
        self.assertEqual(self.ids['fontScale'][1]['min'], '90')
        self.assertEqual(self.ids['fontScale'][1]['max'], '125')
        self.assertEqual(self.ids['commandPalette'][0], 'dialog')

    def test_feature_job_and_profile_review_controls_are_present(self):
        self.assertTrue({'featureReport', 'featureResult', 'featureResultWarnings',
                         'featureResultData', 'featureCopy', 'featureSave', 'featureApply'} <= self.ids.keys())
        self.assertIn('hidden', self.ids['featureApply'][1], 'Profiles require an explicit reviewed Apply action.')
        self.assertIn('hidden', self.ids['featureResult'][1], 'No result should be claimed before an action returns.')
        self.assertEqual(self.ids['featureResultSummary'][1]['role'], 'status')

    def test_plan_approval_and_recipe_requests_use_current_checkbox_selection(self):
        node = shutil.which('node')
        if not node:
            self.skipTest('Optional JavaScript request contract requires Node; no npm packages are needed.')
        options_source = next(line.strip() for line in self.js.splitlines()
                              if line.strip().startswith('function options(){'))
        start = '  async function runFeature(feature){'
        end = '  function saveDownload(download){'
        self.assertIn(start, self.js)
        self.assertIn(end, self.js)
        feature_source = start.strip() + self.js.split(start, 1)[1].split(end, 1)[0]
        empty = {name: False for name in default_options()}
        selected = dict(empty, browser=True, dotnet=True, docs_mcp=True)
        cases = [{'id': feature_id, 'choices': choices, 'report': report}
                 for choices, report in ((empty, ''), (selected, 'known-test-report'))
                 for feature_id in ('f076', 'f078', 'f087')]
        cases.extend({'id': feature_id, 'choices': selected, 'report': 'known-test-report'}
                     for feature_id in ('f077', 'f088'))
        script = """'use strict';
const cases = CASES;
let checkboxes = [], report = '', snapshot = {started:false}, featureBusy = false, quitting = false;
let pauses = 0, clients = 0;
const requests = [], outcomes = [];
const document = {querySelectorAll(selector) {
  if (selector !== '.options input') throw new Error('Unexpected checkbox query');
  return checkboxes;
}};
const $ = id => {
  if (id === 'featureReport') return {value:report};
  if (id === 'featureResult') return {scrollIntoView() {}};
  throw new Error('Unexpected dashboard element: ' + id);
};
const pause = () => {pauses++;};
const renderFeatures = () => {};
const runClientFeature = () => {clients++;};
const showFeatureResult = (feature, state, result, error) => {outcomes.push({id:feature.id,state,error});};
const api = async (path, body) => {
  if (path === 'features/run') {
    requests.push(JSON.parse(JSON.stringify(body)));
    return {id:'test-job'};
  }
  if (path === 'features/jobs/test-job') return {state:'complete',result:{summary:'Contract fixture'}};
  throw new Error('Unexpected API action: ' + path);
};
OPTIONS_SOURCE
FEATURE_SOURCE
(async () => {
  for (const test of cases) {
    checkboxes = Object.entries(test.choices).map(([name,checked]) => ({name,checked}));
    report = test.report;
    await runFeature({id:test.id});
  }
  await runFeature({id:'f091',client:true});
  process.stdout.write(JSON.stringify({requests,outcomes,pauses,clients}));
})().catch(error => {process.stderr.write(error.stack);process.exitCode=1;});
""".replace('CASES', json.dumps(cases)).replace('OPTIONS_SOURCE', options_source).replace('FEATURE_SOURCE', feature_source)
        execution = subprocess.run([node, '-'], input=script, text=True,
                                   capture_output=True, timeout=15, check=False)
        self.assertEqual(execution.returncode, 0, execution.stderr)
        observed = json.loads(execution.stdout)
        self.assertEqual(len(observed['requests']), len(cases))
        for case, request in zip(cases, observed['requests']):
            self.assertEqual(request['id'], case['id'])
            expected = {'options': case['choices']} if case['id'] in ('f076', 'f078', 'f087') else {}
            if case['report']:
                expected['run_id'] = case['report']
            self.assertEqual(request['payload'], expected)
            if 'options' in request['payload']:
                self.assertIs(request['payload']['options']['live'], False)
        self.assertEqual([entry['state'] for entry in observed['outcomes']], ['running', 'complete'] * len(cases))
        self.assertEqual(observed['pauses'], len(cases) + 1)
        self.assertEqual(observed['clients'], 1)


if __name__ == '__main__':
    unittest.main()
