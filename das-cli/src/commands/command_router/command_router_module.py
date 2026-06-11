import os

from common.config.store import JsonConfigStore
from common.container_manager.busnode_container_manager import BusNodeContainerManager
from common.factory.atomdb.atomdb_backend import AtomdbBackend
from common.factory.atomdb.atomdb_factory import AtomDbContainerManagerFactory
from common.factory.busnode_manager_factory import BusNodeContainerManagerFactory
from common.module import Module
from common.settings import Settings
from settings.config import SECRETS_PATH

from .command_router_cli import CommandRouterCli


class CommandRouterModule(Module):
    _instance = CommandRouterCli

    def __init__(self):
        super().__init__()

        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))
        self._bus_node_factory = BusNodeContainerManagerFactory()

        self._dependency_list = [
            (
                BusNodeContainerManager,
                self._bus_node_factory.build(
                    use_settings_from="agents.command_router", service_name="command-router"
                ),
            ),
            (
                AtomdbBackend,
                AtomDbContainerManagerFactory().build(),
            ),
            (Settings, self._settings),
        ]
