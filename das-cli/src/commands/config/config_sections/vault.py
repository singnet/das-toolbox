from common.command import Command
from common.settings import Settings
from common.utils import extract_service_hostname, extract_service_port, require_vault_endpoint

from .setup_utils import get_default_value


def vault_section(settings: Settings):
    default_endpoint = str(get_default_value(settings, "vault.endpoint") or "localhost:8200")

    hostname = Command.prompt(
        "Enter the Vault (OpenBao) hostname (localhost, 127.0.0.1, or 0.0.0.0)",
        default=extract_service_hostname(default_endpoint) or "localhost",
    )
    vault_port = Command.prompt(
        "Enter the Vault (OpenBao) port",
        default=extract_service_port(default_endpoint),
        type=int,
    )

    endpoint = f"{hostname}:{vault_port}"
    require_vault_endpoint(endpoint)
    return {"vault": {"endpoint": endpoint}}
