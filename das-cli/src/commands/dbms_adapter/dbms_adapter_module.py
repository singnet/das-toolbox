import os

from common.factory.atomdb.atomdb_backend import (
    AtomdbBackend,
)

from common.factory.atomdb.atomdb_factory import AtomDbContainerManagerFactory
from common.factory.dbms_peer.das_peer_manager_factory import DasPeerManagerFactory
from common.factory.dbms_peer.dbms_peer_manager_factory import DbmsPeerManagerFactory

from common import Module, Settings
from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH

from .das_peer.das_peer_cli import DasPeerContainerManager
from .dbms_adapter_cli import DbmsAdapterCli
from .dbms_peer.dbms_peer_cli import DbmsPeerContainerManager


class DbmsAdapterModule(Module):
    _instance = DbmsAdapterCli

    def __init__(self) -> None:
        super().__init__()

        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

        self._dependecy_injection = [
            (
                AtomdbBackend,
                AtomDbContainerManagerFactory().build(),
            ),
            (
                DasPeerContainerManager,
                DasPeerManagerFactory().build(),
            ),
            (
                DbmsPeerContainerManager,
                DbmsPeerManagerFactory().build(),
            )
            (
                Settings,
                self._settings,
            ),
        ]

