import os

from common import Settings
from common.config.store import JsonConfigStore
from common.container_manager.vault_container_manager import VaultContainerManager
from common.utils import extract_service_port
from settings.config import SECRETS_PATH


class VaultManagerFactory:
    def __init__(self):
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

    def build(self):
        vault_port = extract_service_port(self._settings.get("vault.endpoint"))
        container_name = f"das-cli-vault-{vault_port}"

        return VaultContainerManager(
            container_name,
            options={
                "vault_port": vault_port,
                "service_name": "Vault",
                "service_command_label": "vault",
            },
        )
