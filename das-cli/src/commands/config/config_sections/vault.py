from common.command import Command
from common.settings import Settings
from common.utils import extract_service_port

from .setup_utils import get_default_value


def vault_section(settings: Settings):
    vault_port = Command.prompt(
        "Enter the Vault (OpenBao) port",
        default=extract_service_port(str(get_default_value(settings, "vault.endpoint"))),
    )

    return {"vault": {"endpoint": f"localhost:{vault_port}"}}
