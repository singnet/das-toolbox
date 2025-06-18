import os

from commands.query_agent.query_agent_container_manager import QueryAgentContainerManager
from common import Module
from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH

from .link_creation_agent_cli import (
    LinkCreationAgentCli,
    LinkCreationAgentContainerManager,
    Settings,
)


class LinkCreationAgentModule(Module):
    _instance = LinkCreationAgentCli

    def __init__(self) -> None:
        super().__init__()

        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

        self._dependecy_injection = [
            (
                LinkCreationAgentContainerManager,
                self._link_creation_agent_container_manager_factory,
            ),
            (
                QueryAgentContainerManager,
                self._query_agent_container_manager_factory,
            ),
            (
                Settings,
                self._settings,
            ),
        ]

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

    def _query_agent_container_manager_factory(self) -> QueryAgentContainerManager:
        query_agent_port = str(self._settings.get("services.query_agent.port"))
        mongodb_hostname = "localhost"
        mongodb_port = self._settings.get("services.mongodb.port")
        mongodb_username = self._settings.get("services.mongodb.username")
        mongodb_password = self._settings.get("services.mongodb.password")

        redis_port = self._settings.get("services.redis.port")
        redis_hostname = "localhost"

        attention_broker_hostname = "localhost"
        attention_broker_port = self._settings.get("services.attention_broker.port")

        container_name = self._settings.get("services.query_agent.container_name")

        return QueryAgentContainerManager(
            container_name,
            options={
                "query_agent_port": query_agent_port,
                "redis_port": redis_port,
                "redis_hostname": redis_hostname,
                "mongodb_port": mongodb_port,
                "mongodb_hostname": mongodb_hostname,
                "mongodb_username": mongodb_username,
                "mongodb_password": mongodb_password,
                "attention_broker_hostname": attention_broker_hostname,
                "attention_broker_port": attention_broker_port,
            },
        )
