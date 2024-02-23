import os
from utils import JsonHandler
from constants import ACTIVE_SERVICES_PATH, SECRETS_PATH


class SecretConfig(JsonHandler):
    _default_config_path = os.path.expanduser(SECRETS_PATH)

    def __init__(self):
        super().__init__(self._default_config_path)


class ActiveServicesConfig(JsonHandler):
    _default_container_path = os.path.expanduser(ACTIVE_SERVICES_PATH)

    def __init__(self):
        super().__init__(self._default_container_path)
