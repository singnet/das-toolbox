from abc import ABC, abstractmethod
from typing import List
from commands.db.mongodb_container_manager import MongodbContainerManager
from commands.db.redis_container_manager import RedisContainerManager

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


class MongoDBRedisBackend(BackendProvider):
    name = "mongodb-redis"

    def __init__(
        self,
        mongodb_container_manager: MongodbContainerManager,
        redis_container_manager: RedisContainerManager,
    ) -> None:
        self._mongodb_container_manager = mongodb_container_manager
        self._redis_container_manager = redis_container_manager

    def start(self) -> None:
        self._mongodb_container_manager.start()
        self._redis_container_manager.start()

    def stop(self) -> None:
        self._redis_container_manager.stop()
        self._mongodb_container_manager.stop()

    def is_running(self) -> bool:
        return (
            self._mongodb_container_manager.is_running()
            and self._redis_container_manager.is_running()
        )


class MorkMongoDBBackend(BackendProvider):
    name = "mork-mongodb"

    def __init__(self, mongodb_container_manager: MongodbContainerManager) -> None:
        self._mongodb_container_manager = mongodb_container_manager

    def start(self) -> None:
        self._mongodb_container_manager.start()

    def stop(self) -> None:
        self._mongodb_container_manager.stop()

    def is_running(self) -> bool:
        return self._mongodb_container_manager.is_running()


class AtomdbBackend:
    def __init__(self, providers: List[BackendProvider]) -> None:
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

    def status(self) -> dict:
        return {p.name: p.is_running() for p in self._providers}
