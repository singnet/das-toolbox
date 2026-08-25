from shared.builders.builder_helpers import _get

DEFAULT_VAULT_ENDPOINT = "localhost:8200"


class VaultBuilder:

    def build(self, vault: dict | None) -> dict:
        vault = vault or {}
        return {"endpoint": _get(vault, "endpoint", DEFAULT_VAULT_ENDPOINT)}
