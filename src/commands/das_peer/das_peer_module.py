from common import Module

from .das_peer_cli import (
    DasPeerCli,
    DasPeerContainerManager,
    Settings,
)

from commands.db.redis_container_manager import RedisContainerManager
from commands.db.mongodb_container_manager import MongodbContainerManager


class DasPeerModule(Module):
    _instance = DasPeerCli

    def __init__(self) -> None:
        super().__init__()

        self._settings = Settings()

        self._dependecy_injection = [
            (
                RedisContainerManager,
                self._redis_container_manager_factory,
            ),
            (
                MongodbContainerManager,
                self._mongodb_container_manager_factory,
            ),
            (
                DasPeerContainerManager,
                self._das_peer_container_manager_factory,
            ),
        ]

    def _mongodb_container_manager_factory(self) -> MongodbContainerManager:
        container_name = self._settings.get("mongodb.container_name")

        return MongodbContainerManager(container_name)

    def _redis_container_manager_factory(self) -> RedisContainerManager:
        container_name = self._settings.get("redis.container_name")

        return RedisContainerManager(container_name)

    def _das_peer_container_manager_factory(
        self,
    ) -> DasPeerContainerManager:
        container_name = self._settings.get("das_peer.container_name")
        mongodb_nodes = self._settings.get("mongodb.nodes")
        mongodb_hostname = mongodb_nodes[0]["ip"] if mongodb_nodes else "host.docker.internal"
        mongodb_username = self._settings.get("mongodb.username")
        mongodb_password = self._settings.get("mongodb.password")
        mongodb_port = self._settings.get("mongodb.port")
        redis_nodes = self._settings.get("redis.nodes")
        redis_hostname = redis_nodes[0]["ip"] if redis_nodes else "host.docker.internal"
        redis_port = self._settings.get("redis.port")

        adapter_server_port = self._settings.get("das_peer.port")

        return DasPeerContainerManager(
            container_name,
            options={
                "das_peer_port": adapter_server_port,
                "mongodb_hostname": mongodb_hostname,
                "mongodb_port": mongodb_port,
                "mongodb_username": mongodb_username,
                "mongodb_password": mongodb_password,
                "redis_hostname": redis_hostname,
                "redis_port": redis_port,
            },
        )
