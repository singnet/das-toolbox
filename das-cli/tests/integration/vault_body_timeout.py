#!/usr/bin/env python3
"""Assert Vault API body-read timeouts become DockerError."""

import socket
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

from common.container_manager.vault_container_manager import VaultContainerManager
from common.docker.exceptions import DockerError


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


def _assert_timeout_is_docker_error(port: int) -> None:
    manager = VaultContainerManager(
        f"das-cli-vault-{port}",
        options={
            "vault_port": port,
            "service_name": "Vault",
            "service_command_label": "vault",
        },
    )
    try:
        manager.get_status()
    except DockerError as error:
        if not isinstance(error.__cause__, TimeoutError):
            cause = type(error.__cause__).__name__ if error.__cause__ is not None else "None"
            raise SystemExit(f"DockerError cause was {cause}") from error
        return
    except Exception as error:
        raise SystemExit(f"expected DockerError, got {type(error).__name__}: {error}") from error

    raise SystemExit("expected DockerError from a stalled HTTP body")


def main() -> None:
    socket.setdefaulttimeout(5)
    _assert_timeout_is_docker_error(_serve_one(200))
    _assert_timeout_is_docker_error(_serve_one(500))


if __name__ == "__main__":
    main()
