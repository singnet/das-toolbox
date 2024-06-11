import os
from common.settings import JsonHandler
from config.config import SECRETS_PATH


class Secret(JsonHandler):
    _default_config_path = os.path.expanduser(SECRETS_PATH)

    def __init__(self):
        super().__init__(self._default_config_path)
