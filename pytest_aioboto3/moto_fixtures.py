from __future__ import annotations  # to allow subscriptable Popen in python >=3.8
import dataclasses
import logging
import shutil
import signal
import socket
import subprocess
import time
from subprocess import Popen
from typing import Any, Iterator, List

import pytest
import requests

_proxy_bypass = {
    "http": None,
    "https": None,
}

logger = logging.getLogger(__name__)


def start_moto_server(service_name: str, host: str, port: int) -> Popen[Any]:
    """
    This originally comes from the tests in aioboto3 that starts up a moto server to test interactions
    at https://github.com/terrycain/aioboto3/blob/92a7a9b8a32615ab6a9ea51ef360475ede94bb1f/tests/mock_server.py
    """
    moto_svr_path = shutil.which("moto_server")
    if not moto_svr_path:
        raise ValueError(
            "Could not find a path to moto_server, is it installed in the virtualenvironment?"
        )
    args = [moto_svr_path, service_name, "-H", host, "-p", str(port)]
    # For debugging
    # args = f"moto_svr_path service_name -H host -p port 2>&1 | tee -a /tmp/moto.log"
    logger.info(f"Starting moto server: {args}")
    process = subprocess.Popen(
        args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )  # shell=True
    url = f"http://{host}:{port}"

    for i in range(0, 30):
        output = process.poll()
        if output is not None:
            print(f"moto_server exited status {output}")
            stdout, stderr = process.communicate()
            print(f"moto_server stdout: {str(stdout)}")
            print(f"moto_server stderr: {str(stderr)}")
            pytest.fail(f"Can not start service: {service_name}")

        try:
            # we need to bypass the proxies due to monkeypatches
            requests.get(url, timeout=5, proxies=_proxy_bypass)  # type: ignore[arg-type]
            break
        except requests.exceptions.ConnectionError:
            time.sleep(0.5)
    else:
        stop_process(process)  # pytest.fail doesn't call stop_process
        pytest.fail("Can not start moto service: {}".format(service_name))

    logger.info(f"Connected to moto server at {url}")

    return process


def stop_process(process: Popen[Any]) -> None:
    try:
        process.send_signal(signal.SIGTERM)
        process.communicate(timeout=20)
    except subprocess.TimeoutExpired:
        process.kill()
        outs, errors = process.communicate(timeout=20)
        exit_code = process.returncode
        msg = "Child process finished {} not in clean way: {} {}".format(exit_code, outs, errors)
        raise RuntimeError(msg)


def get_free_tcp_port() -> int:
    sckt = socket.socket()
    sckt.bind(("", 0))  # binding to 0 gives a new random port
    addr, port = sckt.getsockname()

    # We don't actually need the socket so close it and stop listening
    sckt.close()
    return int(port)


@dataclasses.dataclass(frozen=True)
class MockedAWSService:
    service_name: str
    """AWS service name that you would use when creating a client/resource like 's3' or 'kms' or 'dynamodb'"""
    moto_url: str
    """Url that moto is listening on"""


@pytest.fixture(scope="session")
def moto_services() -> Iterator[List[MockedAWSService]]:
    processes = []
    services = []

    """
    To mock a new AWS service:
    types-aiobotocore = {extras = ["s3"], version = "^2.2.0"}
moto = {extras = ["s3"], version = "^3.1.6"}
boto3-stubs 
    1. Add a new entry to the 'extras' section in pyproject.toml for types-aiobotocore, moto and boto3-stubs like 'dynamodb' or 'ec2'
    2. Add to this tuple the service that you want to mock, the same as the extra you added
    """
    for service in ("s3",):
        host = "localhost"
        port = get_free_tcp_port()
        url = f"http://{host}:{port}"
        processes.append(start_moto_server(service, host, port))
        services.append(MockedAWSService(service, url))

    yield services

    for process in processes:
        try:
            stop_process(process)
        finally:
            # Keep going through exceptions to stop as many as possible
            logger.error(f"Problem stopping moto process {process}")
