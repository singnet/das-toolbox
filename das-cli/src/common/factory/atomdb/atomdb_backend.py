from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional

from common.container_manager.atomdb.mongodb_container_manager import MongodbContainerManager
from common.container_manager.atomdb.morkdb_container_manager import MorkdbContainerManager
from common.container_manager.atomdb.redis_container_manager import RedisContainerManager


class AtomdbBackendEnum(Enum):
    REDIS_MONGODB = "redis_mongodb"
    MORK_MONGODB = "mork_mongodb"

    @classmethod
    def from_value(
        cls,
        value: Optional[str],
        default: Optional["AtomdbBackendEnum"] = None,
    ) -> "AtomdbBackendEnum":
        if default is None:
            default = cls.REDIS_MONGODB
        if value is None:
            return default
        try:
            return cls(value)
        except ValueError:
            return default


class BackendProvider(ABC):
    name: str

    @abstractmethod
    def start(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def is_running(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def status(self) -> list[dict]:
        raise NotImplementedError


class MongoDBRedisBackend(BackendProvider):
    name = AtomdbBackendEnum.REDIS_MONGODB.value

    def __init__(
        self,
        mongodb_container_manager: MongodbContainerManager,
        redis_container_manager: RedisContainerManager,
    ) -> None:
        self._mongodb_container_manager = mongodb_container_manager
        self._redis_container_manager = redis_container_manager

    def start(self) -> None:
        # TODO: Implement this method here to start the database from the backend instance
        raise NotImplementedError

    def stop(self) -> None:
        self._redis_container_manager.stop()
        self._mongodb_container_manager.stop()

    def is_running(self) -> bool:
        return all(
            [
                self._mongodb_container_manager.is_running(),
                self._redis_container_manager.is_running(),
            ]
        )

    def status(self) -> list[dict]:
        return [
            self._mongodb_container_manager.status(),
            self._redis_container_manager.status(),
        ]


class MorkMongoDBBackend(BackendProvider):
    name = AtomdbBackendEnum.MORK_MONGODB.value

    def __init__(
        self,
        mongodb_container_manager: MongodbContainerManager,
        morkdb_container_manager: MorkdbContainerManager,
    ) -> None:
        self._mongodb_container_manager = mongodb_container_manager
        self._mork_db_container_manager = morkdb_container_manager

    def start(self) -> None:
        # TODO: Implement this method here to start the database from the backend instance
        raise NotImplementedError

    def stop(self) -> None:
        self._mongodb_container_manager.stop()
        self._mork_db_container_manager.stop()

    def is_running(self) -> bool:
        return all(
            [
                self._mongodb_container_manager.is_running(),
                self._mork_db_container_manager.is_running(),
            ]
        )

    def status(self) -> list[dict]:
        return [
            self._mongodb_container_manager.status(),
            self._mork_db_container_manager.status(),
        ]


class AtomdbBackend:
    def __init__(self, name: AtomdbBackendEnum, providers: List[BackendProvider]) -> None:
        self.name = name

        self._providers = providers

    def start(self) -> None:
        for provider in self._providers:
            provider.start()

    def stop(self) -> None:
        for provider in self._providers:
            provider.stop()

    def is_running(self) -> bool:
        status = {p.name: p.is_running() for p in self._providers}
        return all(status.values())

    def status(self) -> list[dict]:
        return [status for provider in self._providers for status in provider.status()]

    def get_active_providers(self) -> List[BackendProvider]:
        return self._providers
