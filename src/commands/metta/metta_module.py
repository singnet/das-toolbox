from common import Module

from .metta_cli import MettaCli, Settings, MettaLoaderContainerManager


class MettaModule(Module):
    _instance = MettaCli

    def __init__(self) -> None:
        super().__init__()

        self._settings = Settings()

        self._dependecy_injection = [
            (
                MettaLoaderContainerManager,
                self._metta_loader_container_manager_factory,
            ),
        ]

    def _metta_loader_container_manager_factory(self) -> MettaLoaderContainerManager:
        container_name = self._settings.get("loader.container_name")

        return MettaLoaderContainerManager(container_name)
