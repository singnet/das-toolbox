import os
from typing import List

from common import Settings
from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH

from .atomdb_backend import (
    AtomdbBackend,
    AtomdbBackendEnum,
    BackendProvider,
    InMemoryBackend,
    MongoDBRedisBackend,
    MorkMongoDBBackend,
    RemoteDBBackend,
)
from .mongodb_manager_factory import MongoDbContainerManagerFactory
from .morkdb_manager_factory import MorkDbContainerManagerFactory
from .redis_manager_factory import RedisContainerManagerFactory


class AtomDbContainerManagerFactory:
    def __init__(self):
        self._settings = Settings(
            store=JsonConfigStore(os.path.expanduser(SECRETS_PATH))
        )

    def build(self):
        backend_type = AtomdbBackendEnum.from_value(self._settings.get("atomdb.type"))
        providers = self._build_providers(backend_type)

        return AtomdbBackend(backend_type, providers)

    def _build_providers(
        self,
        backend_type: AtomdbBackendEnum,
    ) -> List[BackendProvider]:

        match backend_type:
            case AtomdbBackendEnum.REDIS_MONGODB:
                return [self._redis_mongodb_backend()]

            case AtomdbBackendEnum.MORK_MONGODB:
                return [self._mork_mongodb_backend()]

            case AtomdbBackendEnum.ADAPTERDB:
                adapter_backend_type = AtomdbBackendEnum.from_value(self._settings.get("atomdb.adapterdb.atomdb_backend.type"))

                return self._build_providers(adapter_backend_type)

            case AtomdbBackendEnum.INMEMORYDB:
                return [InMemoryBackend()]

            case AtomdbBackendEnum.REMOTEDB:
                return [RemoteDBBackend()]

            case _:
                raise ValueError(
                    f"Unsupported AtomDB backend type: {backend_type}"
                )

    def _redis_mongodb_backend(self) -> MongoDBRedisBackend:
        return MongoDBRedisBackend(
            MongoDbContainerManagerFactory().build(),
            RedisContainerManagerFactory().build(),
        )

    def _mork_mongodb_backend(self) -> MorkMongoDBBackend:
        return MorkMongoDBBackend(
            MongoDbContainerManagerFactory().build(),
            MorkDbContainerManagerFactory().build(),
        )