import os
from typing import List

from common.factory.atomdb.atomdb_backend import (
    AtomdbBackend,
)
from common import Module
from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH

from .db_cli import (
    DbCli,
    Settings,
)

from common.factory.atomdb.redis_manager_factory import RedisContainerManagerFactory
from common.factory.atomdb.mongodb_manager_factory import MongoDbContainerManagerFactory
from common.factory.atomdb.morkdb_manager_factory import MorkDbContainerManagerFactory
from common.factory.atomdb.atomdb_factory import AtomDbContainerManagerFactory

from common.container_manager.atomdb.redis_container_manager import RedisContainerManager
from common.container_manager.atomdb.mongodb_container_manager import MongodbContainerManager
from common.container_manager.atomdb.morkdb_container_manager import MorkdbContainerManager


class DbModule(Module):
    _instance = DbCli

    def __init__(self) -> None:
        super().__init__()

        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

        self._dependecy_injection = [
            (
                RedisContainerManager,
                RedisContainerManagerFactory().build()
            ),
            (
                MongodbContainerManager,
                MongoDbContainerManagerFactory().build()
            ),
            (
                AtomdbBackend,
                AtomDbContainerManagerFactory().build(),
            ),
            (
                Settings,
                self._settings,
            ),
            (
                MorkdbContainerManager,
                MorkDbContainerManagerFactory().build()
            ),
        ]
