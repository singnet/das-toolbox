from common.command import Command
from common.settings import Settings
from common.utils import extract_service_port

from .setup_utils import get_default_value


def vault_section(settings: Settings):
    default_endpoint = get_default_value(settings, "vault.endpoint") or "localhost:8200"
    vault_port = Command.prompt(
        "Enter the Vault (OpenBao) port",
        default=extract_service_port(str(default_endpoint)),
        type=int,
    )

    endpoint = f"localhost:{vault_port}"
    return {"vault": {"endpoint": endpoint}}
