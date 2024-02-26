import os
from utils import JsonHandler
from config.config import ACTIVE_SERVICES_PATH


class ActiveServices(JsonHandler):
    _default_container_path = os.path.expanduser(ACTIVE_SERVICES_PATH)

    def __init__(self):
        super().__init__(self._default_container_path)
