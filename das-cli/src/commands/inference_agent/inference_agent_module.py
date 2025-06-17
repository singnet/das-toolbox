import os

from common import Module
from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH

from .inference_agent_cli import (
    InferenceAgentCli,
    InferenceAgentContainerManager,
    LinkCreationAgentContainerManager,
    Settings,
)


class InferenceAgentModule(Module):
    _instance = InferenceAgentCli

    def __init__(self) -> None:
        super().__init__()

        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

        self._dependecy_injection = [
            (
                InferenceAgentContainerManager,
                self._inference_agent_container_manager_factory,
            ),
            (
                LinkCreationAgentContainerManager,
                self._link_creation_agent_container_manager_factory,
            ),
            (
                Settings,
                self._settings,
            ),
        ]

    def _inference_agent_container_manager_factory(self) -> InferenceAgentContainerManager:
        container_name = self._settings.get("services.inference_agent.container_name")

        link_creation_agent_server_hostname = "localhost"
        link_creation_agent_server_port = self._settings.get("services.link_creation_agent.port")

        inference_agent_hostname = "localhost"
        inference_agent_port = self._settings.get("services.inference_agent.port")

        return InferenceAgentContainerManager(
            container_name,
            options={
                "inference_agent_hostname": inference_agent_hostname,
                "inference_agent_port": inference_agent_port,
                "link_creation_agent_server_hostname": link_creation_agent_server_hostname,
                "link_creation_agent_server_port": link_creation_agent_server_port,
                "link_creation_agent_client_hostname": "localhost",
                "link_creation_agent_client_port": 8081,
                "das_client_hostname": "localhost",
                "das_client_port": 8083,
                "das_server_hostname": "localhost",
                "das_server_port": 35500,
                "distributed_inference_control_node_hostname": "localhost",
                "distributed_inference_control_node_port": 8085,
                "distributed_inference_control_node_server_hostname": "localhost",
                "distributed_inference_control_node_server_port": 8086,
            },
        )

    def _link_creation_agent_container_manager_factory(self) -> LinkCreationAgentContainerManager:
        container_name = self._settings.get("services.link_creation_agent.container_name")

        query_agent_server_hostname = "localhost"
        query_agent_server_port = self._settings.get("services.query_agent.port")

        link_creation_agent_server_hostname = "localhost"
        link_creation_agent_server_port = self._settings.get("services.link_creation_agent.port")

        return LinkCreationAgentContainerManager(
            container_name,
            options={
                "query_agent_server_hostname": query_agent_server_hostname,
                "query_agent_server_port": query_agent_server_port,
                "link_creation_agent_server_hostname": link_creation_agent_server_hostname,
                "link_creation_agent_server_port": link_creation_agent_server_port,
                "query_agent_client_hostname": "localhost",
                "query_agent_client_port": 9001,
                "das_agent_client_hostname": "localhost",
                "das_agent_client_port": 9090,
                "das_agent_server_hostname": "localhost",
                "das_agent_server_port": 9091,
            },
        )
