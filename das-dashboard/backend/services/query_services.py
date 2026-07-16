import json

import requests
from fastapi.logger import logger
from requests import Response
from requests.exceptions import RequestException
from websockets.asyncio.client import connect

from shared.exceptions.custom_exceptions import CommandRouterConnectionError, CustomValueError
from shared.internal.constants import LOCAL_HOSTS
from shared.internal.web_configuration import WebConfiguration

VALID_COMMAND_TYPES = ("get", "set", "query")  # Evolution will be disconsidered for now.


class QueryServices:

    def __init__(self, web_config: WebConfiguration):
        self.web_config = web_config

    def health_check_proxy(self) -> Response:
        return self._call_http_proxy("GET", "/ping")

    def get_query_websocket_data(self, execution_id: str):
        try:
            command_proxy_url = self._find_command_router_http_url()
            connect(
                uri=f"ws://{command_proxy_url}/executions/{execution_id}",
                open_timeout=10,
                close_timeout=5,
            )
        except RequestException:
            pass

    def get_query_status(self, execution_id: str) -> Response:
        return self._call_http_proxy("GET", f"/executions/{execution_id}")

    def cancel_query_execution(self, execution_id: str) -> Response:
        return self._call_http_proxy("GET", f"/executions/{execution_id}/cancel")

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
        return self._call_http_proxy(
            "POST",
            "/executions",
            data={"command_type": command_type, "command_text": command_text},
        )

    def _set_query_parameters(self, command_type: str, command_text: str) -> Response:
        custom_parameters_dict = json.loads(command_text)
        response = None

        for key, value in custom_parameters_dict.items():
            response = self._call_http_proxy(
                "POST",
                "/executions",
                data={"command_type": command_type, "command_text": f"param {key} {value}"},
            )

        return response

    def _create_query_execution(self, command_type: str, command_text: str) -> Response:
        return self._call_http_proxy(
            "POST",
            "/executions",
            data={"command_type": command_type, "command_text": command_text},
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
        service_host_map = self.web_config.config_dictionary

        try:
            router_host = service_host_map.get("command-router", None).get("host")

            if router_host is None:
                raise KeyError

            connect_host = "localhost" if router_host in LOCAL_HOSTS else router_host
            return f"{connect_host}:{HTTP_PROXY_PORT}"

        except (AttributeError, KeyError):
            logger.critical("Command Router not found in service/host map.")
            raise
