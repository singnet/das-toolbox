import getpass
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
    def _peer_section(peer: dict, database: str) -> dict:
        section = dict(peer.get(database) or {})
        if section.get("nodes"):
            return section

        endpoint = section.get("endpoint")
        host = endpoint.rsplit(":", 1)[0].strip() if isinstance(endpoint, str) else ""
        if not host or host in {"localhost", "127.0.0.1", "0.0.0.0"}:
            section["nodes"] = [
                {"context": "default", "ip": "localhost", "username": getpass.getuser()}
            ]
        else:
            section["nodes"] = [{"context": "", "ip": host, "username": ""}]
        return section

    def _remote_db_providers(self) -> List[BackendProvider]:
        providers: List[BackendProvider] = []
        for peer in self._settings.get("atomdb.remote_peers", []) or []:
            if not isinstance(peer, dict) or peer.get("type") != "redismongodb":
                continue
            providers.append(
                MongoDBRedisBackend(
                    MongoDbContainerManagerFactory().build(self._peer_section(peer, "mongodb")),
                    RedisContainerManagerFactory().build(self._peer_section(peer, "redis")),
                    peer_uid=peer.get("uid"),
                )
            )
        return providers or [RemoteDBBackend()]

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
