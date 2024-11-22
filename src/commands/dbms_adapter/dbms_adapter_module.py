from common import Module

from .dbms_adapter_cli import DbmsAdapterCli
from common import Module, Settings

from .das_peer.das_peer_cli import DasPeerContainerManager
from .dbms_peer.dbms_peer_cli import DbmsPeerContainerManager

from commands.db.redis_container_manager import RedisContainerManager
from commands.db.mongodb_container_manager import MongodbContainerManager


class DbmsAdapterModule(Module):
    _instance = DbmsAdapterCli

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
            (
                DbmsPeerContainerManager,
                self._dbms_peer_container_manager_factory,
            ),
        ]

    def _mongodb_container_manager_factory(self) -> MongodbContainerManager:
        container_name = self._settings.get("mongodb.container_name")
        port = self._settings.get("mongodb.port")

        return MongodbContainerManager(
            container_name,
            options={
                "mongodb_port": port,
            },
        )

    def _redis_container_manager_factory(self) -> RedisContainerManager:
        container_name = self._settings.get("redis.container_name")
        port = self._settings.get("redis.port")

        return RedisContainerManager(
            container_name,
            options={
                "redis_port": port,
            },
        )

    def _das_peer_container_manager_factory(self) -> DasPeerContainerManager:
        container_name = self._settings.get("das_peer.container_name")
        mongodb_nodes = self._settings.get("mongodb.nodes", [])
        mongodb_hostname = (
            mongodb_nodes[0]["ip"] if len(mongodb_nodes) > 0 else "localhost"
        )
        mongodb_username = self._settings.get("mongodb.username")
        mongodb_password = self._settings.get("mongodb.password")
        mongodb_port = self._settings.get("mongodb.port")
        redis_nodes = self._settings.get("redis.nodes", [])
        redis_hostname = redis_nodes[0]["ip"] if len(redis_nodes) > 0 else "localhost"
        redis_port = self._settings.get("redis.port")

        adapter_server_port = 30100

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

    def _dbms_peer_container_manager_factory(
        self,
    ) -> DbmsPeerContainerManager:
        container_name = self._settings.get("dbms_peer.container_name")
        adapter_server_port = 30100

        return DbmsPeerContainerManager(
            container_name,
            options={
                "das_peer_port": adapter_server_port,
            },
        )
