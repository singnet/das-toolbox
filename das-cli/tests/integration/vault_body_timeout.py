#!/usr/bin/env python3
"""Assert Vault API body-read timeouts become HttpJsonError with a TimeoutError cause.

This helper is stdlib-only so CI can run it with system python3. das-cli is shipped
as a PyInstaller binary, so the runner does not have click/docker installed.
VaultContainerManager._request translates HttpJsonError into DockerError.
"""

import socket
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from http_json import HttpJsonError, request_json


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


def _assert_timeout_is_http_json_error(port: int) -> None:
    try:
        request_json(f"http://127.0.0.1:{port}/v1/sys/seal-status", "GET")
    except HttpJsonError as error:
        if not isinstance(error.__cause__, TimeoutError):
            cause = type(error.__cause__).__name__ if error.__cause__ is not None else "None"
            raise SystemExit(f"HttpJsonError cause was {cause}") from error
        return
    except Exception as error:
        raise SystemExit(f"expected HttpJsonError, got {type(error).__name__}: {error}") from error

    raise SystemExit("expected HttpJsonError from a stalled HTTP body")


def main() -> None:
    socket.setdefaulttimeout(5)
    _assert_timeout_is_http_json_error(_serve_one(200))
    _assert_timeout_is_http_json_error(_serve_one(500))


if __name__ == "__main__":
    main()
