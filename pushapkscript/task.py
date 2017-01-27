import json
import logging
import os

import scriptworker.client
from pushapkscript.exceptions import TaskVerificationError
from pushapkscript.jarsigner import SUPPORTED_CERTIFICATE_ALIAS


log = logging.getLogger(__name__)


def _craft_scope_prefix(scope):
    return ':'.join(('project', 'releng', 'pushapk', scope, ''))    # Leave trailling colon


_SUPPORTED_CHANNELS = ('aurora', 'beta', 'release')
_GOOGLE_PLAY_SCOPE_PREFIX = _craft_scope_prefix('googleplay')
_CERTIFICATE_TYPE_SCOPE_PREFIX = _craft_scope_prefix('cert')


def extract_channel(task):
    return _extract_value_from_scope(task, 'channel', _GOOGLE_PLAY_SCOPE_PREFIX, _SUPPORTED_CHANNELS)


def extract_certificate_type(task):
    return _extract_value_from_scope(task, 'certificate type', _CERTIFICATE_TYPE_SCOPE_PREFIX, SUPPORTED_CERTIFICATE_ALIAS)


def _extract_value_from_scope(task, value_name, prefix, possible_values):
    values = [
        s[len(prefix):]
        for s in task['scopes']
        if s.startswith(prefix)
    ]

    if len(values) != 1:
        raise TaskVerificationError('Only one {0} can be used. {0}s provided: {1}'.format(value_name, values))

    final_value = values[0]
    if final_value not in possible_values:
        raise TaskVerificationError(
            '"{}" is not a supported {}. Value must be in {}'.format(final_value, value_name, possible_values)
        )

    log.info('{}: {}'.format(value_name, final_value))
    return final_value


def validate_task_schema(context):
    with open(context.config['schema_file']) as fh:
        task_schema = json.load(fh)
    log.debug(task_schema)
    scriptworker.client.validate_json_schema(context.task, task_schema)


async def download_files(context):
    payload = context.task['payload']
    apks_to_download = payload['apks']

    # XXX: download_artifacts() takes a list of urls. In order to not loose the association between
    # an apk_type and an apk_url, we set an order once and for all.
    # Warning: This relies on download_artifacts() not changing the order of the files
    ordered_apks = [(apk_type, apk_url) for apk_type, apk_url in apks_to_download.items()]
    file_urls = [apk_url for _, apk_url in ordered_apks]

    # XXX download_artifacts() is imported here, in order to patch it
    from scriptworker.artifacts import download_artifacts
    ordered_files = await download_artifacts(context, file_urls)

    files = {}
    work_dir = context.config['work_dir']
    for i in range(0, len(ordered_apks)):
        apk_type = ordered_apks[i][0]
        apk_relative_path = ordered_files[i]
        files[apk_type] = os.path.join(work_dir, apk_relative_path)

    return files
