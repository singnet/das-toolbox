import os

from shared.exceptions.custom_exceptions import (
    DasCliCommandException,
    ConfigurationFileLoadError,
)
from shared.internal.constants import DEFAULT_SSHKEY_CLONE_PATH, LOCAL_HOSTS
from shared.internal.web_configuration import WebConfiguration
from shared.utils.das_cli_response import (
    DEFAULT_CLI_ERROR_MESSAGE,
    run_das_cli_json_command,
)


def _validate_config_file(file_path: str) -> None:
    import json

    if not os.path.isfile(file_path):
        raise ConfigurationFileLoadError(f"Configuration file not found: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as config_file:
            data = json.load(config_file)
    except json.JSONDecodeError as error:
        raise ConfigurationFileLoadError(
            f"Invalid JSON in configuration file: {error}"
        ) from error
    except OSError as error:
        raise ConfigurationFileLoadError(
            f"Could not read configuration file: {error}"
        ) from error

    if isinstance(data, list):
        if not data:
            raise ConfigurationFileLoadError("Configuration file is empty.")
        data = data[0]

    if not isinstance(data, dict):
        raise ConfigurationFileLoadError("Configuration file must be a JSON object.")

    if "atomdb" not in data or "agents" not in data:
        raise ConfigurationFileLoadError(
            "Configuration file must include 'atomdb' and 'agents' sections."
        )


def set_das_cli_config(
    file_path: str,
    *,
    web_config: WebConfiguration,
    host: str | None = None,
) -> None:
    cleaned_path = (file_path or "").strip()
    if not cleaned_path:
        raise ValueError("Configuration file path is required.")

    remote_host = host if host and host not in LOCAL_HOSTS else None

    if remote_host is None:
        _validate_config_file(cleaned_path)

    cmd = ["das-cli", "config", "set", "--file", cleaned_path, "-o", "json"]

    if remote_host is not None:
        profile = web_config.user_profile
        ssh_username = profile.get("profile_username", "root")
        ssh_key = profile.get("profile_ssh_keypath") or DEFAULT_SSHKEY_CLONE_PATH

        if not os.path.exists(ssh_key):
            raise ValueError("SSH key is not configured. Set up your profile first.")

        cmd.extend(["--remote", "--host", remote_host, "-u", ssh_username, "-k", ssh_key])

    payload = run_das_cli_json_command(
        cmd,
        default_message=DEFAULT_CLI_ERROR_MESSAGE,
        timeout=30,
    )

    details = payload.get("details") or {}
    content = details.get("content")
    if content is not None and not isinstance(content, dict):
        raise DasCliCommandException(
            message="The das-cli config response did not include a valid config object.",
        )
