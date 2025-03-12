from common import Module

from .attention_broker_cli import DbCli, AttentionBrokerManager, Settings


class AttentionBrokerModule(Module):
    _instance = DbCli

    def __init__(self) -> None:
        super().__init__()

        self._settings = Settings()

        self._dependecy_injection = [
            (
                AttentionBrokerManager,
                self._attention_broker_container_manager_factory,
            ),
        ]

    def _attention_broker_container_manager_factory(self) -> AttentionBrokerManager:
        mongodb_hostname = "localhost"
        mongodb_database_name = "das"
        mongodb_port = self._settings.get("mongodb.port")
        mongodb_username = self._settings.get("mongodb.username")
        mongodb_password = self._settings.get("mongodb.password")

        redis_hostname = "localhost" 
        redis_port = self._settings.get("redis.port")

        attention_broker_port = self._settings.get("attention_broker.port")

        container_name = self._settings.get("attention_broker.container_name")

        return AttentionBrokerManager(
            container_name,
            options={
                "mongodb_port": mongodb_port,
                "mongodb_username": mongodb_username,
                "mongodb_password": mongodb_password,
                "mongodb_hostname": mongodb_hostname,
                "mongodb_name": mongodb_database_name,
                "redis_hostname": redis_hostname,
                "redis_port": redis_port,
                "attention_broker_port": attention_broker_port,
            },
        )
