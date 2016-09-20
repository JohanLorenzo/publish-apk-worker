import aiohttp
import asyncio
from asyncio.subprocess import PIPE, STDOUT
from copy import deepcopy
import json
import logging
import os
import random
import traceback

import scriptworker.client
from scriptworker.exceptions import ScriptWorkerException
from scriptworker.utils import retry_async, retry_request
from signingscript.exceptions import SigningServerError, TaskVerificationError
from signingscript.utils import download_file, raise_future_exceptions

log = logging.getLogger(__name__)


def task_cert_type(task):
    """Extract task certificate type"""
    certs = [s for s in task["scopes"] if
             s.startswith("project:releng:signing:cert:")]
    log.info("Certificate types: %s", certs)
    if len(certs) != 1:
        raise TaskVerificationError("Only one certificate type can be used")
    return certs[0]


def task_signing_formats(task):
    """Extract last part of signing format scope"""
    return [s.split(":")[-1] for s in task["scopes"] if
            s.startswith("project:releng:signing:format:")]


def validate_task_schema(context):
    with open(context.config['schema_file']) as fh:
        task_schema = json.load(fh)
    log.debug(task_schema)
    scriptworker.client.validate_json_schema(context.task, task_schema)


def check_mandatory_apks_are_present(apks):
    MANDATORIES = ['armv7_v15', 'x86']
    if not all([mandatory in apks for mandatory in MANDATORIES]):
        print(apks)
        raise Exception('')


async def download_files(context):
    payload = context.task['payload']
    apks_to_download = payload['apks']
    check_mandatory_apks_are_present(apks_to_download)

    work_dir = context.config['work_dir']

    tasks = []
    files = {}
    download_config = deepcopy(context.config)
    download_config.setdefault('valid_artifact_task_ids', context.task['dependencies'])
    for apk_type, apk_url in apks_to_download.items():
        rel_path = scriptworker.client.validate_artifact_url(download_config, apk_url)
        abs_file_path = os.path.join(work_dir, rel_path)
        files[apk_type] = rel_path
        tasks.append(
            asyncio.ensure_future(
                retry_async(download_file, args=(context, apk_url, abs_file_path))
            )
        )

    await raise_future_exceptions(tasks)
    tasks = []
    return files
