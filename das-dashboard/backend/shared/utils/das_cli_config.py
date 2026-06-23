import json
import os
import subprocess

from shared.exceptions.custom_exceptions import DasCliCommandException, DasCliNotInstalledException
from shared.internal.constants import DEFAULT_SSHKEY_CLONE_PATH, LOCAL_HOSTS
from shared.internal.web_configuration import WebConfiguration


def _validate_config_file(file_path: str) -> None:
    if not os.path.isfile(file_path):
        raise ValueError(f"Configuration file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as config_file:
        data = json.load(config_file)

    if isinstance(data, list):
        data = data[0]

    if not isinstance(data, dict):
        raise ValueError("Configuration file must be a JSON object.")

    if "atomdb" not in data or "agents" not in data:
        raise ValueError("Configuration file must include 'atomdb' and 'agents' sections.")


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

    cmd = ["das-cli", "config", "set", "--file", cleaned_path]

    if remote_host is not None:
        profile = web_config.user_profile
        ssh_username = profile.get("profile_username", "root")
        ssh_key = profile.get("profile_ssh_keypath") or DEFAULT_SSHKEY_CLONE_PATH

        if not os.path.exists(ssh_key):
            raise ValueError("SSH key is not configured. Set up your profile first.")

        cmd.extend(["--remote", "--host", remote_host, "-u", ssh_username, "-k", ssh_key])

    try:
        subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError as error:
        raise DasCliNotInstalledException("das-cli not found.") from error
    except subprocess.CalledProcessError as error:
        error_output = (error.stderr or error.stdout or "Unknown Subprocess Error").strip()
        raise DasCliCommandException(error_output) from error
    except Exception as error:
        raise DasCliCommandException(str(error)) from error
