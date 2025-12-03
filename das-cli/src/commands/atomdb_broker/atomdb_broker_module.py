import os
from typing import List

from commands.db.atomdb_backend import (
    AtomdbBackend,
    AtomdbBackendEnum,
    BackendProvider,
    MongoDBRedisBackend,
    MorkMongoDBBackend,
)
from commands.db.mongodb_container_manager import MongodbContainerManager
from commands.db.morkdb_container_manager import MorkdbContainerManager
from commands.db.redis_container_manager import RedisContainerManager
from common import Module, Settings
from common.bus_node.busnode_container_manager import BusNodeContainerManager
from common.bus_node.busnode_manager_factory import BusNodeContainerManagerFactory
from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH

from .atomdb_broker_cli import AtomDbBrokerCli


class AtomDbBrokerModule(Module):
    _instance = AtomDbBrokerCli

    def __init__(self):
        super().__init__()

        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))
        self._bus_node_factory = BusNodeContainerManagerFactory()

        self._dependecy_injection = [
            (
                BusNodeContainerManager,
                self._bus_node_factory.build(
                    use_settings="atomdb_broker", service_name="atomdb-broker"
                ),
            ),
            (
                AtomdbBackend,
                self._atom_db_backend_factory,
            ),
            (
                Settings,
                self._settings,
            ),
        ]

        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

    def _redis_container_manager_factory(self) -> RedisContainerManager:
        container_name = self._settings.get("services.redis.container_name")
        redis_port = self._settings.get("services.redis.port")

        return RedisContainerManager(
            container_name,
            options={
                "redis_port": redis_port,
            },
        )

    def _mongodb_container_manager_factory(self) -> MongodbContainerManager:
        container_name = self._settings.get("services.mongodb.container_name")
        mongodb_port = self._settings.get("services.mongodb.port")
        mongodb_username = self._settings.get("services.mongodb.username")
        mongodb_password = self._settings.get("services.mongodb.password")

        return MongodbContainerManager(
            container_name,
            options={
                "mongodb_port": mongodb_port,
                "mongodb_username": mongodb_username,
                "mongodb_password": mongodb_password,
            },
        )

    def _morkdb_container_manager_factory(self) -> MorkdbContainerManager:
        container_name = self._settings.get("services.morkdb.container_name")
        morkdb_port = self._settings.get("services.morkdb.port")

        return MorkdbContainerManager(
            container_name,
            options={
                "morkdb_port": morkdb_port,
            },
        )

    def _atom_db_backend_factory(self) -> AtomdbBackend:
        backend_name = self._settings.get("services.database.atomdb_backend")
        providers: List[BackendProvider] = []
        backend_name = AtomdbBackendEnum.from_value(backend_name)

        if backend_name == AtomdbBackendEnum.REDIS_MONGODB:
            providers.append(
                MongoDBRedisBackend(
                    self._mongodb_container_manager_factory(),
                    self._redis_container_manager_factory(),
                ),
            )
        elif backend_name == AtomdbBackendEnum.MORK_MONGODB:
            providers.append(
                MorkMongoDBBackend(
                    self._mongodb_container_manager_factory(),
                    self._morkdb_container_manager_factory(),
                )
            )

        return AtomdbBackend(backend_name, providers)
