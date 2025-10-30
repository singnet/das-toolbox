import os

from typing import List
from commands.db.mongodb_container_manager import MongodbContainerManager
from commands.db.redis_container_manager import RedisContainerManager
from commands.db.morkdb_container_manager import MorkdbContainerManager
from common import Module, Settings
from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH

from .das_peer.das_peer_cli import DasPeerContainerManager
from .dbms_adapter_cli import DbmsAdapterCli
from .dbms_peer.dbms_peer_cli import DbmsPeerContainerManager

from commands.db.atomdb_backend import (
    AtomdbBackend,
    BackendProvider,
    MongoDBRedisBackend,
    MorkMongoDBBackend,
)

class DbmsAdapterModule(Module):
    _instance = DbmsAdapterCli

    def __init__(self) -> None:
        super().__init__()

        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

        self._dependecy_injection = [
            (
                AtomdbBackend,
                self._atomdb_backend_factory,
            ),
            (
                DasPeerContainerManager,
                self._das_peer_container_manager_factory,
            ),
            (
                DbmsPeerContainerManager,
                self._dbms_peer_container_manager_factory,
            ),
            (
                Settings,
                self._settings,
            ),
        ]

    def _mongodb_container_manager_factory(self) -> MongodbContainerManager:
        container_name = self._settings.get("services.mongodb.container_name")
        port = self._settings.get("services.mongodb.port")

        return MongodbContainerManager(
            container_name,
            options={
                "mongodb_port": port,
            },
        )

    def _redis_container_manager_factory(self) -> RedisContainerManager:
        container_name = self._settings.get("services.redis.container_name")
        port = self._settings.get("services.redis.port")

        return RedisContainerManager(
            container_name,
            options={
                "redis_port": port,
            },
        )

    def _das_peer_container_manager_factory(self) -> DasPeerContainerManager:
        container_name = self._settings.get("services.das_peer.container_name")
        mongodb_nodes = self._settings.get("services.mongodb.nodes", [])
        mongodb_container_name = self._settings.get("services.mongodb.container_name")
        mongodb_hostname = (
            mongodb_nodes[0]["ip"] if len(mongodb_nodes) > 1 else mongodb_container_name
        )
        mongodb_username = self._settings.get("services.mongodb.username")
        mongodb_password = self._settings.get("services.mongodb.password")
        mongodb_port = self._settings.get("services.mongodb.port")
        redis_nodes = self._settings.get("services.redis.nodes", [])
        redis_container_name = self._settings.get("services.redis.container_name")
        redis_hostname = redis_nodes[0]["ip"] if len(redis_nodes) > 1 else redis_container_name
        redis_port = self._settings.get("services.redis.port")

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
        container_name = self._settings.get("services.dbms_peer.container_name")
        adapter_server_port = 30100

        return DbmsPeerContainerManager(
            container_name,
            options={
                "das_peer_port": adapter_server_port,
            },
        )

    def _atomdb_backend_factory(self) -> AtomdbBackend:
        backend_name = self._settings.get("services.database.atomdb_backend")
        providers: List[BackendProvider] = []

        if backend_name == "redis_mongodb":
            providers.append(
                MongoDBRedisBackend(
                    self._mongodb_container_manager_factory(),
                    self._redis_container_manager_factory(),
                ),
            )
        elif backend_name == "mork_mongodb":
            providers.append(
                MorkMongoDBBackend(
                    self._morkdb_container_manager_factory(),
                    self._mongodb_container_manager_factory(),
                )
            )

        return AtomdbBackend(providers)

    def _morkdb_container_manager_factory(self) -> MorkdbContainerManager:
        container_name = self._settings.get("services.morkdb.container_name")
        morkdb_port = self._settings.get("services.morkdb.port")

        return MorkdbContainerManager(
            container_name,
            options={
                "morkdb_port": morkdb_port,
            },
        )
