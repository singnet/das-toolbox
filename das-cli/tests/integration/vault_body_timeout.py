#!/usr/bin/env python3
"""Assert Vault API body-read timeouts become DockerError with a TimeoutError cause.

This helper is stdlib-only so CI can run it with system python3. das-cli is shipped
as a PyInstaller binary, so the runner does not have click/docker installed.
VaultContainerManager._request is loaded from source with those imports stubbed.
"""

import importlib.util
import socket
import sys
import threading
import time
import types
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


def _stub_runtime_modules() -> None:
    docker = types.ModuleType("docker")
    docker.errors = types.ModuleType("docker.errors")
    docker.errors.APIError = type("APIError", (Exception,), {})
    docker.errors.NotFound = type("NotFound", (Exception,), {})
    sys.modules.setdefault("docker", docker)
    sys.modules.setdefault("docker.errors", docker.errors)

    common = types.ModuleType("common")
    common.Container = type("Container", (), {"__init__": lambda self, *args, **kwargs: None})
    common.ContainerManager = type(
        "ContainerManager", (), {"__init__": lambda self, *args, **kwargs: None}
    )
    sys.modules.setdefault("common", common)

    docker_pkg = types.ModuleType("common.docker")
    exceptions = types.ModuleType("common.docker.exceptions")
    exceptions.DockerError = type("DockerError", (Exception,), {})
    exceptions.DockerContainerNotFoundError = type(
        "DockerContainerNotFoundError",
        (exceptions.DockerError,),
        {},
    )
    sys.modules.setdefault("common.docker", docker_pkg)
    sys.modules.setdefault("common.docker.exceptions", exceptions)

    settings = types.ModuleType("settings")
    config = types.ModuleType("settings.config")
    config.DAS_PATH = Path("/tmp")
    config.OPENBAO_IMAGE_NAME = "openbao/openbao"
    config.OPENBAO_IMAGE_VERSION = "2.6.1"
    sys.modules.setdefault("settings", settings)
    sys.modules.setdefault("settings.config", config)


def _load_vault_container_manager():
    _stub_runtime_modules()
    path = (
        Path(__file__).resolve().parents[2]
        / "src"
        / "common"
        / "container_manager"
        / "vault_container_manager.py"
    )
    spec = importlib.util.spec_from_file_location("vault_container_manager", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class StallingHandler(BaseHTTPRequestHandler):
    status_code = 200

    def do_GET(self) -> None:
        self.send_response(self.status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", "1000")
        self.end_headers()
        time.sleep(30)

    def log_message(self, _format: str, *_args) -> None:
        return


def _serve_one(status_code: int) -> int:
    StallingHandler.status_code = status_code
    server = HTTPServer(("127.0.0.1", 0), StallingHandler)
    port = int(server.server_address[1])
    thread = threading.Thread(target=server.handle_request, daemon=True)
    thread.start()
    return port


def _assert_timeout_is_docker_error(module, port: int) -> None:
    class Client:
        def get_container(self):
            return type("Container", (), {"port": port})()

        _read_json = staticmethod(module.VaultContainerManager._read_json)

    try:
        module.VaultContainerManager._request(Client(), "GET", "/v1/sys/seal-status")
    except module.DockerError as error:
        if not isinstance(error.__cause__, TimeoutError):
            cause = type(error.__cause__).__name__ if error.__cause__ is not None else "None"
            raise SystemExit(f"DockerError cause was {cause}") from error
        return
    except Exception as error:
        raise SystemExit(f"expected DockerError, got {type(error).__name__}: {error}") from error

    raise SystemExit("expected DockerError from a stalled HTTP body")


def main() -> None:
    socket.setdefaulttimeout(5)
    module = _load_vault_container_manager()
    _assert_timeout_is_docker_error(module, _serve_one(200))
    _assert_timeout_is_docker_error(module, _serve_one(500))


if __name__ == "__main__":
    main()
