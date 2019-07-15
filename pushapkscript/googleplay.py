import logging

from mozapkpublisher.common.googleplay import GooglePlayConnection, MockGooglePlayConnection, RolloutTrack, StaticTrack
from mozapkpublisher.push_apk import push_apk

log = logging.getLogger(__name__)

_DEFAULT_TRACK_VALUES = ['production', 'beta', 'alpha', 'rollout', 'internal']


def publish_to_googleplay(payload, product_config, publish_config, apk_files, contact_google_play):
    if contact_google_play:
        connection = GooglePlayConnection.open(
            publish_config['service_account'],
            publish_config['google_credentials_file']
        )
    else:
        connection = MockGooglePlayConnection()

    if publish_config['google_play_track'] == 'rollout':
        track = RolloutTrack(publish_config['rollout_percentage'] / 100.0)
    else:
        track = StaticTrack(publish_config['google_play_track'])

    push_apk(
        apks=apk_files,
        connection=connection,
        track=track,
        expected_package_names=publish_config['package_names'],
        commit=should_commit_transaction(payload),
        skip_check_ordered_version_codes=bool(product_config.get('skip_check_ordered_version_codes')),
        skip_check_multiple_locales=bool(product_config.get('skip_check_multiple_locales')),
        skip_check_same_locales=bool(product_config.get('skip_check_same_locales')),
        skip_checks_fennec=bool(product_config.get('skip_checks_fennec')),
    )


def should_commit_transaction(task_payload):
    # Don't commit anything by default. Committed APKs can't be unpublished,
    # unless you push a newer set of APKs.
    return task_payload.get('commit', False)
