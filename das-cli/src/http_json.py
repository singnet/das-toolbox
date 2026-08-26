import json
import urllib.error
import urllib.request
from typing import Any


class HttpJsonError(Exception):
    """Raised when a JSON HTTP request fails, including body-read timeouts."""


def request_json(
    url: str,
    method: str,
    body: dict[str, Any] | None = None,
    timeout: float = 5,
) -> tuple[int, dict[str, Any]]:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = urllib.request.Request(url, data=data, method=method)
    if data is not None:
        request.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, _read_json(response.read())
    except urllib.error.HTTPError as error:
        try:
            raw = error.read()
        except TimeoutError as timeout_error:
            raise HttpJsonError(str(timeout_error)) from timeout_error
        payload = _read_json(raw)
        errors = payload.get("errors")
        if errors:
            raise HttpJsonError("; ".join(str(item) for item in errors))
        raise HttpJsonError(str(error))
    except urllib.error.URLError as error:
        raise HttpJsonError(str(error.reason)) from error
    except TimeoutError as timeout_error:
        raise HttpJsonError(str(timeout_error)) from timeout_error


def _read_json(raw: bytes) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        payload = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as error:
        raise HttpJsonError(f"Unexpected Vault API response: {error}") from error

    if not isinstance(payload, dict):
        raise HttpJsonError("Unexpected Vault API response.")
    return payload
