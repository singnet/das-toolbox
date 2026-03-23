import os

from common import Settings
from common.config.store import JsonConfigStore
from common.container_manager.atomdb.redis_container_manager import RedisContainerManager
from settings.config import SECRETS_PATH
from common.utils import extract_service_port
from common.config.core import get_core_defaults_dict

class RedisContainerManagerFactory:

    def __init__(self):
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))
        self._default = get_core_defaults_dict()

    def build(self):
        redis_port = extract_service_port(self._settings.get("atomdb.redis.endpoint"))
        container_name = f"das-cli-redis-{redis_port}"
        return RedisContainerManager(
            container_name,
            options={
                "redis_port": redis_port,
            },
        )
