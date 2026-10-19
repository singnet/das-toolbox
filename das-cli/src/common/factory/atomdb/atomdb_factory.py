import os
from typing import List
from urllib.parse import urlsplit

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
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

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
                adapter_backend_type = AtomdbBackendEnum.from_value(
                    self._settings.get("atomdb.adapterdb.atomdb_backend.type")
                )

                return self._build_providers(adapter_backend_type)

            case AtomdbBackendEnum.INMEMORYDB:
                return [InMemoryBackend()]

            case AtomdbBackendEnum.REMOTEDB:
                return self._remote_db_providers()

            case _:
                raise ValueError(f"Unsupported AtomDB backend type: {backend_type}")

    @staticmethod
    def _is_local_endpoint(endpoint) -> bool:
        return isinstance(endpoint, str) and urlsplit(f"//{endpoint}").hostname in {
            "localhost", "127.0.0.1", "0.0.0.0"
        }

    def _remote_db_providers(self) -> List[BackendProvider]:
        local_peers = []
        for peer in self._settings.get("atomdb.remote_peers", []) or []:
            if peer.get("type") != "redismongodb":
                continue
            redis_local = self._is_local_endpoint(peer.get("redis", {}).get("endpoint"))
            mongo_local = self._is_local_endpoint(peer.get("mongodb", {}).get("endpoint"))
            if redis_local != mongo_local:
                raise ValueError("The local peer must use local endpoints for both databases")
            if redis_local:
                local_peers.append(peer)
        if not local_peers:
            return [RemoteDBBackend()]
        if len(local_peers) != 1:
            raise ValueError("RemoteDB supports only one local RedisMongo peer")
        peer = local_peers[0]
        for database in ("redis", "mongodb"):
            metadata = self._settings.get(f"atomdb.{database}", {}) or {}
            endpoint = metadata.get("endpoint")
            if not self._is_local_endpoint(endpoint) or not metadata.get("nodes"):
                raise ValueError("Missing local database metadata; save the RemoteDB configuration again")
            if urlsplit(f"//{endpoint}").port != urlsplit(f"//{peer[database]['endpoint']}").port:
                raise ValueError("Local database metadata does not match the local peer")
        mongodb = self._settings.get("atomdb.mongodb", {})
        if any(mongodb.get(key) != peer["mongodb"].get(key) for key in ("username", "password")):
            raise ValueError("Local MongoDB credentials do not match the local peer")
        return [self._redis_mongodb_backend()]

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
