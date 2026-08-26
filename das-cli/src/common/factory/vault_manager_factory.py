import os

from common import Settings
from common.config.core import get_core_defaults_dict
from common.config.store import JsonConfigStore
from common.container_manager.vault_container_manager import (
    VAULT_CONTAINER_NAME,
    VaultContainerManager,
)
from common.utils import extract_service_port
from settings.config import SECRETS_PATH


class VaultManagerFactory:
    def __init__(self):
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

    def build(self):
        endpoint = self._settings.get("vault.endpoint")
        if not endpoint:
            endpoint = get_core_defaults_dict()["vault"]["endpoint"]

        vault_port = extract_service_port(endpoint)

        return VaultContainerManager(
            VAULT_CONTAINER_NAME,
            options={
                "vault_port": vault_port,
                "service_name": "Vault",
                "service_command_label": "vault",
            },
        )
