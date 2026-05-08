import os

from common import Module
from common.config.store import JsonConfigStore
from common.container_manager.system_containers_manager import SystemContainersManager
from common.factory.system_containers_factory import SystemContainerManagerFactory
from common.settings import Settings
from common.systemutils.sys_info import SystemInfoExtractor
from settings.config import SECRETS_PATH

from .system_cli import SystemCli


class SystemModule(Module):
    _instance = SystemCli

    def __init__(self) -> None:
        super().__init__()

        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))
        self._system_extractor = SystemInfoExtractor()
        
        self._dependency_list = [
            (SystemContainersManager, SystemContainerManagerFactory().build()),
            (SystemInfoExtractor, self._system_extractor),
            (Settings, self._settings),
        ]        
