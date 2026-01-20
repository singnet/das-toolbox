import os
from settings.config import SECRETS_PATH
from common import Settings
from common.config.store import JsonConfigStore
from .mongodb_manager_factory import MongoDbContainerManagerFactory
from .morkdb_manager_factory import MorkDbContainerManagerFactory
from .redis_manager_factory import RedisContainerManagerFactory
from .atomdb_backend import AtomdbBackend, AtomdbBackendEnum, MongoDBRedisBackend, MorkMongoDBBackend

class AtomDbContainerManagerFactory:

    def __init__(self):
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

    def build(self):

        backend_config = self._settings.get("services.database.atomdb_backend")
        backend_config = AtomdbBackendEnum.from_value(backend_config)

        if backend_config == AtomdbBackendEnum.REDIS_MONGODB:
            providers = [MongoDBRedisBackend(MongoDbContainerManagerFactory().build(), RedisContainerManagerFactory().build())]

            return AtomdbBackend(backend_config, providers)
                
        elif backend_config == AtomdbBackendEnum.MORK_MONGODB:
            providers = [MorkMongoDBBackend(MongoDbContainerManagerFactory().build(), MorkDbContainerManagerFactory().build())]

            return AtomdbBackend(backend_config, providers)