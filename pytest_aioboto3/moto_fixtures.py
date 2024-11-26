from __future__ import annotations

import logging
import shutil
import signal
import socket
import subprocess
import time
from subprocess import Popen
from typing import Any, Iterator, Mapping

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
    # args = f"moto_svr_path service_name -H host -p port 2>&1 | tee -a /tmp/moto.log"  # noqa: ERA001
    logger.info(f"Starting moto server: {args}")
    process = subprocess.Popen(
        args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )  # shell=True
    url = f"http://{host}:{port}"

    for _ in range(30):
        output = process.poll()
        if output is not None:
            logger.error(f"moto_server exited status {output}")
            stdout, stderr = process.communicate()
            logger.error(f"moto_server stdout: {stdout!s}")
            logger.error(f"moto_server stderr: {stderr!s}")
            pytest.fail(f"Can not start service: {service_name}")

        try:
            # we need to bypass the proxies due to monkeypatches
            requests.get(url, timeout=5, proxies=_proxy_bypass)  # type: ignore[arg-type]
            break
        except requests.exceptions.ConnectionError:
            time.sleep(0.5)
    else:
        stop_process(process)  # pytest.fail doesn't call stop_process
        pytest.fail(f"Can not start moto service: {service_name}")

    logger.info(f"Connected to moto server at {url}")

    return process


def stop_process(process: Popen[Any]) -> None:
    try:
        process.send_signal(signal.SIGTERM)
        process.communicate(timeout=20)
    except subprocess.TimeoutExpired as te:
        process.kill()
        outs, errors = process.communicate(timeout=20)
        exit_code = process.returncode
        msg = f"Child process finished {exit_code} not in clean way: {outs} {errors}"
        raise RuntimeError(msg) from te


def get_free_tcp_port() -> int:
    sckt = socket.socket()
    sckt.bind(("", 0))  # binding to 0 gives a new random port
    addr, port = sckt.getsockname()

    # We don't actually need the socket so close it and stop listening
    sckt.close()
    return int(port)


@pytest.fixture(scope="session")
def moto_services() -> Iterator[Mapping[str, str]]:
    """
    Map of mocked services with moto where the key is the service name and the value is the moto url to that service
    """
    processes = []
    services: dict[str, str] = {}
    """

    1. Add a new entry to the 'extras' section in pyproject.toml for types-aiobotocore, moto and boto3-stubs like 'dynamodb' or 'ec2'
    2. Add to this tuple the service that you want to mock, the same as the extra you added
    """
    for service in ("s3",):
        host = "localhost"
        port = get_free_tcp_port()
        url = f"http://{host}:{port}"
        processes.append(start_moto_server(service, host, port))
        services[service] = url

    yield services

    for process in processes:
        try:
            stop_process(process)
            logger.info(f"Stopped moto process {process.pid}")
        except Exception:
            # Keep going through exceptions to stop as many as possible
            logger.exception(f"Problem stopping moto process {process}")
