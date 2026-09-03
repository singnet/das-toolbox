import asyncio
import importlib
import json
from typing import Any

import requests
from requests.exceptions import RequestException

from common.settings import Settings

TERMINAL_STATUSES = frozenset({"completed", "error", "aborted"})
ROUTER_TIMEOUT_SECONDS = 10


class CommandRouterQueryClient:
    def __init__(self, settings: Settings):
        self._settings = settings

    def create_execution(self, query_text: str, parameters: dict[str, Any] | None = None) -> dict:
        payload = self._build_query_execution_payload(query_text=query_text, parameters=parameters)
        url = f"{self._build_http_base_url()}/command-router/executions"

        try:
            response = requests.post(url, json=payload, timeout=ROUTER_TIMEOUT_SECONDS)
            response.raise_for_status()
            return response.json()
        except RequestException as error:
            raise RuntimeError(f"Failed to create query execution on {url}: {error}") from error
        except ValueError as error:
            raise RuntimeError(f"Command-router returned invalid JSON for execution creation: {error}") from error

    async def stream_events(self, execution_id: str):
        endpoints = self._build_websocket_urls(execution_id)
        last_error: Exception | None = None
        ws_connect, ws_exception = self._load_websocket_client()

        for endpoint in endpoints:
            try:
                async with ws_connect(endpoint, open_timeout=10, close_timeout=5) as upstream:
                    async for raw_message in upstream:
                        event = self._transform_stream_event(json.loads(raw_message))
                        yield event

                        if event.get("status") in TERMINAL_STATUSES:
                            return

                return
            except (ws_exception, OSError, asyncio.TimeoutError, json.JSONDecodeError) as error:
                last_error = error

        message = str(last_error) if last_error else "unknown websocket error"
        raise RuntimeError(
            f"Failed to stream execution events from command-router for execution '{execution_id}': {message}"
        ) from last_error

    def _load_websocket_client(self):
        try:
            ws_client_module = importlib.import_module("websockets.asyncio.client")
            ws_exceptions_module = importlib.import_module("websockets.exceptions")
        except ModuleNotFoundError as error:
            raise RuntimeError(
                "Missing dependency 'websockets'. Install dependencies and try again."
            ) from error

        return ws_client_module.connect, ws_exceptions_module.WebSocketException

    def _build_http_base_url(self) -> str:
        return f"http://{self._resolve_http_api_endpoint()}"

    def _build_websocket_urls(self, execution_id: str) -> list[str]:
        endpoint = self._resolve_http_api_endpoint()
        return [
            f"ws://{endpoint}/executions/ws/{execution_id}",
            f"ws://{endpoint}/command-router/ws/{execution_id}",
        ]

    def _resolve_http_api_endpoint(self) -> str:
        explicit_http_api = self._settings.get("agents.command_router.http_api.endpoint", None)
        if explicit_http_api:
            return explicit_http_api

        router_endpoint = self._settings.get("agents.command_router.endpoint", "localhost:40008")
        host = str(router_endpoint).split(":", maxsplit=1)[0]
        return f"{host}:40009"

    def _build_query_execution_payload(
        self,
        query_text: str,
        parameters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        trimmed_query = query_text.strip()
        if not trimmed_query:
            raise ValueError("Query text must not be empty.")

        payload_params: dict[str, Any] = {
            "query": {
                "syntax": "metta",
                "tokens": [trimmed_query],
            }
        }

        if parameters:
            if "query" in parameters:
                raise ValueError("Reserved parameter 'query' cannot be overridden.")
            payload_params.update(parameters)

        return {
            "command": "query",
            "params": payload_params,
        }

    def _transform_stream_event(self, event: dict[str, Any]) -> dict[str, Any]:
        command = event.get("command")
        params = event.get("params")

        if command == "query_answers" and isinstance(params, dict):
            return {
                "execution_id": params.get("execution_id") or event.get("execution_id"),
                "type": "chunk",
                "seq": params.get("seq"),
                "received_count": params.get("received_count"),
                "data": params.get("answers", []),
            }

        if command == "execution_status" and isinstance(params, dict):
            transformed = {
                "execution_id": params.get("execution_id"),
                "status": params.get("status"),
            }
            if params.get("message"):
                transformed["message"] = params.get("message")
            if params.get("total_items") is not None:
                transformed["received_count"] = params.get("total_items")
            elif params.get("received_count") is not None:
                transformed["received_count"] = params.get("received_count")
            return transformed

        return event
