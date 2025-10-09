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

        link_creation_agent_hostname = self._settings.get("services.link_creation_agent.hostname")
        link_creation_agent_port = self._settings.get("services.link_creation_agent.port")
        link_creation_agent_buffer_file = self._settings.get(
            "services.link_creation_agent.buffer_file"
        )
        link_creation_agent_request_interval = self._settings.get(
            "services.link_creation_agent.request_interval", 1
        )
        link_creation_agent_thread_count = self._settings.get(
            "services.link_creation_agent.thread_count", 1
        )
        link_creation_agent_default_timeout = self._settings.get(
            "services.link_creation_agent.default_timeout", 10
        )
        link_creation_agent_save_links_to_metta_file = self._settings.get(
            "services.link_creation_agent.save_links_to_metta_file", True
        )
        link_creation_agent_save_links_to_db = self._settings.get(
            "services.link_creation_agent.save_links_to_db", True
        )

        mongodb_hostname = self._settings.get("services.mongodb.hostname")
        mongodb_port = self._settings.get("services.mongodb.port")
        mongodb_username = self._settings.get("services.mongodb.username")
        mongodb_password = self._settings.get("services.mongodb.password")

        redis_port = self._settings.get("services.redis.port")
        redis_hostname = self._settings.get("services.redis.hostname")
        redis_cluster = self._settings.get("services.redis.cluster", False)

        attention_broker_hostname = self._settings.get("services.attention_broker.hostname")
        attention_broker_port = self._settings.get("services.attention_broker.port")

        return LinkCreationAgentContainerManager(
            container_name,
            options={
                "link_creation_agent_hostname": link_creation_agent_hostname,
                "link_creation_agent_port": link_creation_agent_port,
                "link_creation_agent_buffer_file": link_creation_agent_buffer_file,
                "link_creation_agent_request_interval": link_creation_agent_request_interval,
                "link_creation_agent_thread_count": link_creation_agent_thread_count,
                "link_creation_agent_default_timeout": link_creation_agent_default_timeout,
                "link_creation_agent_save_links_to_metta_file": link_creation_agent_save_links_to_metta_file,
                "link_creation_agent_save_links_to_db": link_creation_agent_save_links_to_db,
                "redis_port": redis_port,
                "redis_hostname": redis_hostname,
                "redis_cluster": redis_cluster,
                "mongodb_port": mongodb_port,
                "mongodb_hostname": mongodb_hostname,
                "mongodb_username": mongodb_username,
                "mongodb_password": mongodb_password,
                "attention_broker_hostname": attention_broker_hostname,
                "attention_broker_port": attention_broker_port,
            },
        )

    def _query_agent_container_manager_factory(self) -> QueryAgentContainerManager:
        query_agent_port = str(self._settings.get("services.query_agent.port"))
        mongodb_hostname = self._settings.get("services.mongodb.hostname")
        mongodb_port = self._settings.get("services.mongodb.port")
        mongodb_username = self._settings.get("services.mongodb.username")
        mongodb_password = self._settings.get("services.mongodb.password")

        redis_port = self._settings.get("services.redis.port")
        redis_hostname = self._settings.get("services.redis.hostname")

        attention_broker_hostname = self._settings.get("services.attention_broker.hostname")
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
