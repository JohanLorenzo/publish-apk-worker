import logging
import subprocess

from pushapkscript.exceptions import SignatureError
from pushapkscript.task import SUPPORTED_CHANNELS

log = logging.getLogger(__name__)

CERTIFICATE_ALIASES = {
    'aurora': 'nightly',
    'beta': 'nightly',
    'release': 'release'
}
# Make sure no alias channel is missing in the dict
assert tuple(sorted(CERTIFICATE_ALIASES.keys())) == SUPPORTED_CHANNELS


def verify(context, apk_path, channel):
    binary_path, keystore_path = _pluck_configuration(context)
    certificate_alias = CERTIFICATE_ALIASES[channel]

    completed_process = subprocess.run([
        binary_path, '-verify', '-strict',
        '-keystore', keystore_path,
        apk_path,
        certificate_alias
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

    if completed_process.returncode != 0:
        log.critical(completed_process.stdout)
        raise SignatureError(
            '{} doesn\'t verify apk "{}". It compared certificate against "{}", located in keystore "{}"'
            .format(binary_path, apk_path, certificate_alias, keystore_path)
        )


def _pluck_configuration(context):
    keystore_path = context.config['jarsigner_key_store']
    # Uses jarsigner in PATH if config doesn't provide it
    binary_path = context.config.get('jarsigner_binary', 'jarsigner')

    return binary_path, keystore_path
