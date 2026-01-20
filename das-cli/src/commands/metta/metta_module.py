import os
from typing import List

from common.factory.atomdb.atomdb_backend import (
    AtomdbBackend,
)

from common import Module
from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH

from common.factory.atomdb.atomdb_factory import AtomDbContainerManagerFactory

from common.container_manager.morkdb_container_manager import MorkdbContainerManager
from common.container_manager.metta_loader_container_manager import MettaLoaderContainerManager
from common.container_manager.metta_mork_loader_container_manager import MettaMorkLoaderContainerManager

from common.factory.metta.metta_loader_manager_factory import MettaLoaderManagerFactory
from common.factory.metta.metta_mork_loader_manager_factory import MettaMorkLoaderManagerFactory

from common.factory.atomdb.atomdb_factory import MorkDbContainerManagerFactory

from .metta_cli import (
    MettaCli,
    Settings,
)


class MettaModule(Module):
    _instance = MettaCli

    def __init__(self) -> None:
        super().__init__()

        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

        self._dependecy_injection = [
            (
                AtomdbBackend,
                AtomDbContainerManagerFactory().build()
            ),
            (
                MettaLoaderContainerManager,
                MettaLoaderManagerFactory().build()
            ),
            (
                MorkdbContainerManager,
                MorkDbContainerManagerFactory().build()
            ),
            (
                Settings,
                self._settings,
            ),
            (
                MettaMorkLoaderContainerManager,
                MettaMorkLoaderManagerFactory().build()
            ),
        ]
