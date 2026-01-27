import os

from common import Module
from common.config.store import JsonConfigStore
from common.container_manager.atomdb.morkdb_container_manager import MorkdbContainerManager
from common.container_manager.metta.metta_loader_container_manager import (
    MettaLoaderContainerManager,
)
from common.container_manager.metta.metta_mork_loader_container_manager import (
    MettaMorkLoaderContainerManager,
)
from common.factory.atomdb.atomdb_backend import (
    AtomdbBackend,
)
from common.factory.atomdb.atomdb_factory import (
    AtomDbContainerManagerFactory,
    MorkDbContainerManagerFactory,
)
from common.factory.metta.metta_loader_manager_factory import MettaLoaderManagerFactory
from common.factory.metta.metta_mork_loader_manager_factory import MettaMorkLoaderManagerFactory
from settings.config import SECRETS_PATH

from .metta_cli import (
    MettaCli,
    Settings,
)


class MettaModule(Module):
    _instance = MettaCli

    def __init__(self) -> None:
        super().__init__()

        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

        self._dependency_list = [
            (AtomdbBackend, AtomDbContainerManagerFactory().build()),
            (MettaLoaderContainerManager, MettaLoaderManagerFactory().build()),
            (MorkdbContainerManager, MorkDbContainerManagerFactory().build()),
            (
                Settings,
                self._settings,
            ),
            (MettaMorkLoaderContainerManager, MettaMorkLoaderManagerFactory().build()),
        ]
