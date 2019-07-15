import unittest

from unittest.mock import patch

from mozapkpublisher.common.googleplay import MockGooglePlayConnection, RolloutTrack, StaticTrack

from pushapkscript.googleplay import publish_to_googleplay, should_commit_transaction
from pushapkscript.test.helpers.mock_file import MockFile


# TODO: refactor to pytest instead of unittest
@patch('pushapkscript.googleplay.GooglePlayConnection.open')
@patch('pushapkscript.googleplay.push_apk')
class GooglePlayTest(unittest.TestCase):
    def setUp(self):
        self.publish_config = {
            'google_play_track': 'beta',
            'package_names': ['org.mozilla.fennec_aurora'],
            'service_account': 'service_account',
            'google_credentials_file': '/google_credentials.p12',
        }
        self.apks = [MockFile('/path/to/x86.apk'), MockFile('/path/to/arm_v15.apk')]

    def test_publish_config(self, mock_push_apk, mock_open):
        mock_open.return_value = 'GooglePlayConnection'
        publish_to_googleplay({}, {}, self.publish_config, self.apks, contact_google_play=True)

        mock_push_apk.assert_called_with(
            apks=[MockFile('/path/to/x86.apk'), MockFile('/path/to/arm_v15.apk')],
            connection='GooglePlayConnection',
            track=StaticTrack('beta'),
            expected_package_names=['org.mozilla.fennec_aurora'],
            commit=False,
            skip_check_multiple_locales=False,
            skip_check_ordered_version_codes=False,
            skip_check_same_locales=False,
            skip_checks_fennec=False,
        )

    def test_publish_allows_rollout_percentage(self, mock_push_apk, _):
        publish_config = {
            'google_play_track': 'rollout',
            'rollout_percentage': 10,
            'package_names': ['org.mozilla.fennec_aurora'],
            'service_account': 'service_account',
            'google_credentials_file': '/google_credentials.p12',
        }
        publish_to_googleplay({}, {}, publish_config, self.apks, contact_google_play=True)
        _, args = mock_push_apk.call_args
        assert args['track'] == RolloutTrack(0.10)

    def test_craft_push_config_allows_to_contact_google_play(self, mock_push_apk, mock_open):
        mock_open.return_value = 'GooglePlayConnection'
        publish_to_googleplay({}, {}, self.publish_config, self.apks, contact_google_play=True)
        _, args = mock_push_apk.call_args
        mock_open.assert_called_once()
        assert args['connection'] == 'GooglePlayConnection'

    def test_craft_push_config_allows_to_not_contact_google_play(self, mock_push_apk, mock_open):
        publish_to_googleplay({}, {}, self.publish_config, self.apks, contact_google_play=False)
        _, args = mock_push_apk.call_args
        mock_open.assert_not_called()
        assert isinstance(args['connection'], MockGooglePlayConnection)

    def test_craft_push_config_skip_checking_multiple_locales(self, mock_push_apk, _):
        product_config = {
            'skip_check_multiple_locales': True,
        }
        publish_to_googleplay({}, product_config, self.publish_config, self.apks, contact_google_play=True)
        _, args = mock_push_apk.call_args
        assert args['skip_check_multiple_locales'] is True

    def test_craft_push_config_skip_checking_same_locales(self, mock_push_apk, _):
        product_config = {
            'skip_check_same_locales': True,
        }
        publish_to_googleplay({}, product_config, self.publish_config, self.apks, contact_google_play=True)
        _, args = mock_push_apk.call_args
        assert args['skip_check_same_locales'] is True

    def test_craft_push_config_expect_package_names(self, mock_push_apk, _):
        publish_config = {
            'google_play_track': 'beta',
            'package_names': ['org.mozilla.focus', 'org.mozilla.klar'],
            'service_account': 'service_account',
            'google_credentials_file': '/google_credentials.p12',
        }
        publish_to_googleplay({}, {}, publish_config, self.apks, contact_google_play=True)
        _, args = mock_push_apk.call_args
        assert args['expected_package_names'] == ['org.mozilla.focus', 'org.mozilla.klar']

    def test_craft_push_config_allows_committing_apks(self, mock_push_apk, _):
        task_payload = {
            'commit': True
        }
        publish_to_googleplay(task_payload, {}, self.publish_config, self.apks, contact_google_play=True)
        _, args = mock_push_apk.call_args
        assert args['commit'] is True


def test_should_commit_transaction():
    task_payload = {
        'commit': True
    }
    assert should_commit_transaction(task_payload) is True

    task_payload = {
        'commit': False
    }
    assert should_commit_transaction(task_payload) is False

    task_payload = {}
    assert should_commit_transaction(task_payload) is False
