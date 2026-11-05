import os

from common import Settings
from common.config.defaults import get_default_config_dict
from common.config.store import JsonConfigStore
from common.container_manager.vault_container_manager import (
    VAULT_CONTAINER_NAME,
    VaultContainerManager,
)
from common.utils import require_vault_endpoint
from settings.config import SECRETS_PATH


class VaultManagerFactory:
    def __init__(self):
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

    def build(self):
        endpoint = self._settings.get("vault.endpoint")
        if not endpoint:
            endpoint = get_default_config_dict().get("vault", {}).get("endpoint", "localhost:40010")

        _, vault_port = require_vault_endpoint(endpoint)

        return VaultContainerManager(
            VAULT_CONTAINER_NAME,
            options={
                "vault_port": vault_port,
                "service_name": "Vault",
                "service_command_label": "vault",
            },
        )
