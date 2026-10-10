"""Privacy and review contracts for the optional report-explanation interface."""
from html.parser import HTMLParser
from pathlib import Path
import unittest


class DashboardParser(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.elements = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))


class AiDashboardContracts(unittest.TestCase):
    def setUp(self):
        self.html = (Path(__file__).resolve().parents[1] / 'index.html').read_text(encoding='utf-8-sig')
        self.elements = DashboardParser(self.html).elements
        self.ids = {attrs['id']: (tag, attrs) for tag, attrs in self.elements if 'id' in attrs}

    def test_external_request_requires_two_initially_unchecked_consents(self):
        for identity in ('aiReviewed', 'aiFreeAccount'):
            tag, attrs = self.ids[identity]
            self.assertEqual(tag, 'input')
            self.assertEqual(attrs['type'], 'checkbox')
            self.assertNotIn('checked', attrs)
        self.assertIn('disabled', self.ids['aiAsk'][1])
        self.assertIn('I reviewed this excerpt and allow sending it to this provider.', self.html)
        self.assertIn('free-tier key/account with billing disabled', self.html)

    def test_cloud_key_input_is_optional_session_only_and_not_autocompleted(self):
        self.assertEqual(self.ids['aiEnvKey'][0], 'code')
        self.assertEqual(self.ids['aiKeyStatus'][0], 'dd')
        password_fields = [attrs for tag, attrs in self.elements if tag == 'input' and attrs.get('type') == 'password']
        self.assertEqual(len(password_fields), 1)
        self.assertEqual(password_fields[0]['id'], 'aiSessionKey')
        self.assertEqual(password_fields[0]['autocomplete'], 'off')
        self.assertEqual(password_fields[0]['maxlength'], '4096')
        self.assertIn('never saved in browser storage, reports or the repository', self.html)
        self.assertLess(self.html.index('id="aiCloudOptions"'), self.html.index('id="aiSessionKey"'))

    def test_preview_and_advice_use_plaintext_review_surfaces(self):
        self.assertEqual(self.ids['aiExcerpt'][0], 'pre')
        self.assertEqual(self.ids['aiResultText'][0], 'pre')
        self.assertIn('hidden', self.ids['aiPreviewPanel'][1])
        self.assertIn('hidden', self.ids['aiResultPanel'][1])
        self.assertIn('UNVERIFIED ADVICE', self.html)
        self.assertIn('does not execute suggested commands', self.html)
        self.assertIn('no automatic retries or provider fallback', self.html)

    def test_optional_panel_labels_and_navigation_remain_accessible(self):
        self.assertTrue(any(tag == 'a' and attrs.get('href') == '#aiStudio'
                            for tag, attrs in self.elements))
        self.assertEqual(self.ids['aiStudio'][1]['aria-labelledby'], 'ai-title')
        self.assertEqual(self.ids['aiStatus'][1]['role'], 'status')
        self.assertTrue(any(tag == 'label' and attrs.get('for') == 'aiProvider'
                            for tag, attrs in self.elements))
        self.assertEqual(self.ids['aiDocs'][1]['rel'], 'noreferrer')

    def test_built_in_guidance_is_visible_and_cloud_options_are_closed_by_default(self):
        self.assertNotIn('hidden', self.ids['aiLocalAsk'][1])
        self.assertEqual(self.ids['aiCloudOptions'][0], 'details')
        self.assertNotIn('open', self.ids['aiCloudOptions'][1])
        self.assertIn('Works without an account, API key or upload.', self.html)
        self.assertIn('rather than a local language model', self.html)


if __name__ == '__main__':
    unittest.main()
