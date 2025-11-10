import os

from common import Module
from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH

from .inference_agent_cli import (
    AttentionBrokerManager,
    InferenceAgentCli,
    InferenceAgentContainerManager,
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
                AttentionBrokerManager,
                self._attention_broker_container_manager_factory,
            ),
            (
                Settings,
                self._settings,
            ),
        ]

    def _inference_agent_container_manager_factory(self) -> InferenceAgentContainerManager:
        container_name = self._settings.get("services.inference_agent.container_name")

        inference_agent_port = self._settings.get("services.inference_agent.port")

        mongodb_port = self._settings.get("services.mongodb.port")
        mongodb_username = self._settings.get("services.mongodb.username")
        mongodb_password = self._settings.get("services.mongodb.password")

        redis_port = self._settings.get("services.redis.port")

        morkdb_port = self._settings.get("services.morkdb.port")

        atomdb_backend = self._settings.get("services.database.atomdb_backend")

        attention_broker_port = self._settings.get("services.attention_broker.port")

        return InferenceAgentContainerManager(
            container_name,
            options={
                "inference_agent_hostname": "0.0.0.0",
                "inference_agent_port": inference_agent_port,
                "redis_port": redis_port,
                "redis_hostname": "0.0.0.0",
                "mongodb_port": mongodb_port,
                "mongodb_hostname": "0.0.0.0",
                "mongodb_username": mongodb_username,
                "mongodb_password": mongodb_password,
                "attention_broker_hostname": "0.0.0.0",
                "attention_broker_port": attention_broker_port,
                "atomdb_backend": atomdb_backend,
                "morkdb_port": morkdb_port,
                "morkdb_hostname": "0.0.0.0",
            },
        )

    def _attention_broker_container_manager_factory(self) -> AttentionBrokerManager:
        attention_broker_port = str(self._settings.get("services.attention_broker.port"))

        container_name = self._settings.get("services.attention_broker.container_name")

        return AttentionBrokerManager(
            container_name,
            options={
                "attention_broker_port": attention_broker_port,
            },
        )
