from zipfile import ZipFile

from pushapkscript.exceptions import TaskVerificationError

from mozapkpublisher.apk import get_apk_architecture

_DIRECTORY_WITH_ARCHITECTURE_METADATA = 'lib/'     # For instance: lib/x86/ or lib/armeabi-v7a/
_ARCHITECTURE_SUBDIRECTORY_INDEX = len(_DIRECTORY_WITH_ARCHITECTURE_METADATA.split('/')) - 1    # Removes last trailing slash

_EXPECTED_MOZAPKPUBLISHER_ARCHITECTURES_PER_CHANNEL = {
    # XXX arm64-v8a to come in Aurora (Bug 1368484)
    'aurora': ('armv7_v15', 'x86'),
    'beta': ('armv7_v15', 'x86'),
    'release': ('armv7_v15', 'x86'),
}


def sort_and_check_apks_per_architectures(apks_paths, channel):
    apks_per_architectures = {
        _convert_architecture_to_mozapkpublisher(get_apk_architecture(apk_path)): apk_path
        for apk_path in apks_paths
    }

    _check_architectures_are_valid(apks_per_architectures.keys(), channel)

    return apks_per_architectures


def _convert_architecture_to_mozapkpublisher(architecture):
    return 'armv7_v15' if architecture == 'armeabi-v7a' else architecture


def _check_architectures_are_valid(mozapkpublisher_architectures, channel):
    try:
        expected_architectures = _EXPECTED_MOZAPKPUBLISHER_ARCHITECTURES_PER_CHANNEL[channel]
    except KeyError:
        raise TaskVerificationError('"{}" is not an expected channel. Allowed values: {}'.format(
            channel, _EXPECTED_MOZAPKPUBLISHER_ARCHITECTURES_PER_CHANNEL.keys()
        ))

    are_all_architectures_present = all(
        expected_architecture in mozapkpublisher_architectures
        for expected_architecture in expected_architectures
    )

    if not are_all_architectures_present:
        raise TaskVerificationError('One or many architecture are missing. Detected architectures: {}. Expected architecture: {}'
                                    .format(mozapkpublisher_architectures, expected_architectures))

    if len(mozapkpublisher_architectures) > len(expected_architectures):
        raise TaskVerificationError('Unsupported architectures detected. Detected architectures: {}. Expected architecture: {}'
                                    .format(mozapkpublisher_architectures, expected_architectures))
