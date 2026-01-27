import os
from typing import List

from common import Settings
from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH

from .atomdb_backend import (
    AtomdbBackend,
    AtomdbBackendEnum,
    BackendProvider,
    MongoDBRedisBackend,
    MorkMongoDBBackend,
)
from .mongodb_manager_factory import MongoDbContainerManagerFactory
from .morkdb_manager_factory import MorkDbContainerManagerFactory
from .redis_manager_factory import RedisContainerManagerFactory


class AtomDbContainerManagerFactory:

    def __init__(self):
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

    def build(self):

        backend_config = self._settings.get("services.database.atomdb_backend")
        backend_config = AtomdbBackendEnum.from_value(backend_config)

        if backend_config == AtomdbBackendEnum.REDIS_MONGODB:
            mongoredis_providers: List[BackendProvider] = [
                MongoDBRedisBackend(
                    MongoDbContainerManagerFactory().build(), RedisContainerManagerFactory().build()
                )
            ]

            return AtomdbBackend(backend_config, mongoredis_providers)

        elif backend_config == AtomdbBackendEnum.MORK_MONGODB:
            mongomork_providers: List[BackendProvider] = [
                MorkMongoDBBackend(
                    MongoDbContainerManagerFactory().build(),
                    MorkDbContainerManagerFactory().build(),
                )
            ]

            return AtomdbBackend(backend_config, mongomork_providers)
