import unittest
import engine

class DotnetChannelTests(unittest.TestCase):
    def test_go_live_rc_is_still_a_development_channel(self):
        data={'releases-index':[{'channel-version':'11.0','support-phase':'go-live','latest-sdk':'11.0.100-rc.1.26425.128'},{'channel-version':'10.0','support-phase':'active','latest-sdk':'10.0.401'}]}
        self.assertEqual(engine.choose_dotnet_channel(data),'11.0')

    def test_newest_development_channel_selected_over_older_rc(self):
        data={'releases-index':[{'channel-version':'11.0','support-phase':'go-live','latest-sdk':'11.0.100-rc.1'},{'channel-version':'12.0','support-phase':'preview','latest-sdk':'12.0.100-preview.1'}]}
        self.assertEqual(engine.choose_dotnet_channel(data),'12.0')

    def test_stable_or_malformed_channels_are_never_substituted(self):
        for phase,sdk,channel in [('active','11.0.100','11.0'),('go-live','11.0.100','11.0'),('preview','11.0.100-rc.1','../11.0')]:
            with self.subTest(phase=phase,sdk=sdk),self.assertRaises(engine.OperationError):
                engine.choose_dotnet_channel({'releases-index':[{'channel-version':channel,'support-phase':phase,'latest-sdk':sdk}]})
