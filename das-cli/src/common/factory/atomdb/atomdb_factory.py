import os
from settings.config import SECRETS_PATH
from common import Settings
from common.config.store import JsonConfigStore
from .mongodb_manager_factory import MongoDbContainerManagerFactory
from .morkdb_manager_factory import MorkDbContainerManagerFactory
from .redis_manager_factory import RedisContainerManagerFactory
from commands.db.atomdb_backend import MongoDBRedisBackend, MorkMongoDBBackend

class AtomDbContainerManagerFactory:

    def __init__(self):
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

    def build(self):
        atomdb_backend = self._settings.get("services.database.atomdb_backend")

        if atomdb_backend == "redis_mongodb":
            return MongoDBRedisBackend(
                MongoDbContainerManagerFactory().build(),
                RedisContainerManagerFactory().build(),
            )
        
        elif atomdb_backend == "mork_mongodb":
            return MorkMongoDBBackend(
                MongoDbContainerManagerFactory().build(),
                MorkDbContainerManagerFactory().build(),
            )