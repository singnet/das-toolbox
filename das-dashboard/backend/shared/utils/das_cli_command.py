import shlex

from shared.internal.constants import DEFAULT_SSHKEY_CLONE_PATH, LOCAL_HOSTS
from shared.internal.web_configuration import WebConfiguration


def build_host_cli_command(
    web_config: WebConfiguration, host: str, arguments: list[str]
) -> list[str]:
    command = ["das-cli", *arguments]
    if host in LOCAL_HOSTS:
        return command

    profile = web_config.user_profile
    return [
        "ssh",
        "-T",
        "-o", "BatchMode=yes",
        "-o", "IdentitiesOnly=yes",
        "-o", "StrictHostKeyChecking=accept-new",
        "-o", "ConnectTimeout=15",
        "-o", "ServerAliveInterval=15",
        "-o", "ServerAliveCountMax=2",
        "-i", profile.get("profile_ssh_keypath") or DEFAULT_SSHKEY_CLONE_PATH,
        "-l", profile.get("profile_username") or "root",
        "--", host,
        shlex.join(command),
    ]