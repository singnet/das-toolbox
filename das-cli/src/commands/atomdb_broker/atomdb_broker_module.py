import os

from common import Module, Settings
from common.config.store import JsonConfigStore
from common.container_manager.busnode_container_manager import BusNodeContainerManager
from common.factory.atomdb.atomdb_backend import (
    AtomdbBackend,
)
from common.factory.atomdb.atomdb_factory import AtomDbContainerManagerFactory
from common.factory.busnode_manager_factory import BusNodeContainerManagerFactory
from settings.config import SECRETS_PATH

from .atomdb_broker_cli import AtomDbBrokerCli


class AtomDbBrokerModule(Module):
    _instance = AtomDbBrokerCli

    def __init__(self):
        super().__init__()

        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))
        self._bus_node_factory = BusNodeContainerManagerFactory()

        self._dependency_list = [
            (
                BusNodeContainerManager,
                self._bus_node_factory.build(
                    use_settings="atomdb_broker", service_name="atomdb-broker"
                ),
            ),
            (
                AtomdbBackend,
                AtomDbContainerManagerFactory().build(),
            ),
            (
                Settings,
                self._settings,
            ),
        ]

        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))
