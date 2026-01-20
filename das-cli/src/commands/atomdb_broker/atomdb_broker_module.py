import os
from typing import List

from common.factory.atomdb.atomdb_backend import (
    AtomdbBackend,
)

from common.factory.atomdb.atomdb_factory import AtomDbContainerManagerFactory

from common import Module, Settings
from common.bus_node.busnode_container_manager import BusNodeContainerManager
from common.bus_node.busnode_manager_factory import BusNodeContainerManagerFactory
from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH

from .atomdb_broker_cli import AtomDbBrokerCli


class AtomDbBrokerModule(Module):
    _instance = AtomDbBrokerCli

    def __init__(self):
        super().__init__()

        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))
        self._bus_node_factory = BusNodeContainerManagerFactory()

        self._dependecy_injection = [
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
