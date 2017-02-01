import logging
import subprocess

from pushapkscript.exceptions import SignatureError

log = logging.getLogger(__name__)

SUPPORTED_CERTIFICATE_ALIAS = ('nightly', 'release')


def verify(context, apk_path, certificate_alias):
    binary_path, keystore_path = _pluck_configuration(context)

    if certificate_alias not in SUPPORTED_CERTIFICATE_ALIAS:
        raise SignatureError('Unknown certificate alias: {}. Please choose between: {}'.format(certificate_alias, SUPPORTED_CERTIFICATE_ALIAS))

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
