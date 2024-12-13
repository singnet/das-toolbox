import os

from common.settings import JsonHandler
from config.config import get_config


class Secret(JsonHandler):
    _default_config_path = os.path.expanduser(get_config("SECRETS_PATH"))

    def __init__(self):
        super().__init__(self._default_config_path)
