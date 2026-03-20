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
    InMemoryBackend,
    RemoteDBBackend,
)
from .mongodb_manager_factory import MongoDbContainerManagerFactory
from .morkdb_manager_factory import MorkDbContainerManagerFactory
from .redis_manager_factory import RedisContainerManagerFactory


class AtomDbContainerManagerFactory:

    def __init__(self):
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

    def build(self):

        backend_config = self._settings.get("atomdb.type")
        backend_config = AtomdbBackendEnum.from_value(backend_config)

        providers : List[BackendProvider] = []

        if backend_config == AtomdbBackendEnum.REDIS_MONGODB:
            providers = [
                MongoDBRedisBackend(
                    MongoDbContainerManagerFactory().build(), RedisContainerManagerFactory().build()
                )
            ]

        elif backend_config == AtomdbBackendEnum.MORK_MONGODB:
            providers = [
                MorkMongoDBBackend(
                    MongoDbContainerManagerFactory().build(),
                    MorkDbContainerManagerFactory().build(),
                )
            ]

        elif backend_config == AtomdbBackendEnum.INMEMORYDB:
            providers = [InMemoryBackend()]

        elif backend_config == AtomdbBackendEnum.REMOTEDB:
            providers = [RemoteDBBackend()]

        return AtomdbBackend(backend_config, providers)