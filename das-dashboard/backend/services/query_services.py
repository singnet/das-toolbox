import json
from collections.abc import AsyncIterator
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from requests import Response
from requests.exceptions import RequestException
from websockets.asyncio.client import connect

from shared.db import query_db
from shared.exceptions.custom_exceptions import CommandRouterConnectionError, CustomValueError
from shared.internal.constants import LOCAL_HOSTS
from shared.internal.web_configuration import WebConfiguration
from shared.utils.parse_query_answer import transform_stream_event

VALID_COMMAND_TYPES = ("get", "set", "query")  # Evolution will be disconsidered for now.
ROUTE_PREFIX = "/command-router"

class QueryServices:

    def __init__(self, web_config: WebConfiguration):
        self.web_config = web_config

    def health_check_proxy(self) -> Response:
        return self._call_http_proxy("GET", "/ping")

    async def stream_execution_events(self, execution_id: str) -> AsyncIterator[dict]:
        websocket_url = self._build_websocket_url(execution_id)

        try:
            async with connect(
                websocket_url,
                open_timeout=10,
                close_timeout=5,
            ) as upstream:
                async for message in upstream:
                    payload = transform_stream_event(json.loads(message))
                    query_db.save_event(execution_id, payload)
                    if payload.get("type") == "chunk":
                        query_db.save_answers_from_chunk(execution_id, payload)
                    yield payload
        except RequestException as error:
            raise CommandRouterConnectionError(endpoint=websocket_url, detail=str(error)) from error
        except OSError as error:
            raise CommandRouterConnectionError(endpoint=websocket_url, detail=str(error)) from error

    def get_query_status(self, execution_id: str) -> Response:
        return self._call_http_proxy("GET", f"{ROUTE_PREFIX}/executions/{execution_id}")

    def get_execution_answers(
        self,
        execution_id: str,
        page: int = 1,
        page_size: int = 10,
    ) -> dict:
        return query_db.get_answers_page(execution_id, page, page_size)

    def cancel_query_execution(self, execution_id: str) -> Response:
        return self._call_http_proxy("POST", f"{ROUTE_PREFIX}/executions/{execution_id}/cancel")

    def execute_proxy_command(self, command_type: str, command_text: str) -> Response:
        handlers = {
            "get": self._get_query_parameters,
            "set": self._set_query_parameters,
            "query": self._create_query_execution,
        }

        if command_type not in VALID_COMMAND_TYPES:
            raise CustomValueError(
                "This proxy command does not exist/is not permitted in the current context."
            )

        return handlers[command_type](command_type, command_text)

    def _get_query_parameters(self, command_type: str, command_text: str) -> Response:
        return self._post_execution(command_type, command_text)

    def _set_query_parameters(self, command_type: str, command_text: str) -> Response:
        custom_parameters_dict = json.loads(command_text)
        if not custom_parameters_dict:
            raise CustomValueError("No query parameters were provided.")

        responses = []
        max_workers = min(len(custom_parameters_dict), 8)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(
                    self._post_execution,
                    command_type,
                    f"param {key} {self._format_param_value(value)}",
                )
                for key, value in custom_parameters_dict.items()
            ]

            for future in as_completed(futures):
                responses.append(future.result())

        failed_response = next(
            (response for response in responses if response.status_code >= 400),
            None,
        )
        if failed_response is not None:
            return failed_response

        return responses[-1]

    def get_default_params_from_config(self) -> dict:
        config = self.web_config.load_raw_configuration()
        agents = config.get("agents") or {}

        defaults = dict(agents.get("base_query", {}).get("params", {}))

        query = dict(agents.get("query") or {})
        query.pop("endpoint", None)
        query.pop("ports_range", None)

        query_params = query.get("params") or {}
        if isinstance(query_params, dict):
            defaults.update(query_params)

        return defaults

    @staticmethod
    def _format_param_value(value) -> str:
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value)

    def _create_query_execution(self, command_type: str, command_text: str) -> Response:
        return self._post_execution(command_type, command_text)

    def _post_execution(self, command_type: str, command_text: str) -> Response:
        return self._call_http_proxy(
            "POST",
            f"{ROUTE_PREFIX}/executions",
            json={"command_type": command_type, "command_text": command_text},
        )

    def _call_http_proxy(self, method: str, path: str, **request_kwargs) -> Response:
        command_proxy_url = self._find_command_router_http_url()
        url = f"http://{command_proxy_url}{path}"

        try:
            return requests.request(method, url, timeout=5, **request_kwargs)
        except RequestException as error:
            raise CommandRouterConnectionError(endpoint=url, detail=str(error)) from error

    def _find_command_router_http_url(self) -> str:
        HTTP_PROXY_PORT = 40009
        router = self.web_config.get_service_config("command-router")
        router_host = router["host"]
        connect_host = "localhost" if router_host in LOCAL_HOSTS else router_host
        return f"{connect_host}:{HTTP_PROXY_PORT}"

    def _build_websocket_url(self, execution_id: str) -> str:
        return f"ws://{self._find_command_router_http_url()}{ROUTE_PREFIX}/ws/{execution_id}"
