import os

from common import Settings
from common.config.store import JsonConfigStore
from common.container_manager.atomdb.redis_container_manager import RedisContainerManager
from settings.config import SECRETS_PATH


class RedisContainerManagerFactory:

    def __init__(self):
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

    def build(self):
        container_name = self._settings.get("services.redis.container_name")
        redis_port = self._settings.get("services.redis.port")
        return RedisContainerManager(
            container_name,
            options={
                "redis_port": redis_port,
            },
        )
