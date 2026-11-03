import os

import paramiko

from shared.internal.web_configuration import WebConfiguration
from shared.utils.remote_scp import RemoteScpService

SSH_CONFIG_BLOCK_START = "# BEGIN das-dashboard docker contexts"
SSH_CONFIG_BLOCK_END = "# END das-dashboard docker contexts"


def ensure_docker_ssh_access(web_config: WebConfiguration, hosts: list[str]) -> None:
    """Lets das-cli SSH Docker contexts reach the hosts with the dashboard profile key.

    The Docker SDK reads the key from ~/.ssh/config and rejects hosts missing from
    ~/.ssh/known_hosts, so both files must cover every host.
    """
    hosts = sorted(set(hosts))
    if not hosts:
        return

    remote_scp = RemoteScpService(web_config)
    username, key_path = remote_scp.ensure_profile()

    ssh_dir = os.path.expanduser("~/.ssh")
    os.makedirs(ssh_dir, mode=0o700, exist_ok=True)

    _write_ssh_config(os.path.join(ssh_dir, "config"), hosts, username, key_path)
    _add_known_hosts(remote_scp, os.path.join(ssh_dir, "known_hosts"), hosts)


def _write_ssh_config(path: str, hosts: list[str], username: str, key_path: str) -> None:
    lines: list[str] = []
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as config_file:
            lines = config_file.read().splitlines()

    kept: list[str] = []
    inside_block = False
    for line in lines:
        if line.strip() == SSH_CONFIG_BLOCK_START:
            inside_block = True
            continue
        if line.strip() == SSH_CONFIG_BLOCK_END:
            inside_block = False
            continue
        if not inside_block:
            kept.append(line)

    block = [
        SSH_CONFIG_BLOCK_START,
        f"Host {' '.join(hosts)}",
        f"    User {username}",
        f"    IdentityFile {key_path}",
        "    IdentitiesOnly yes",
        SSH_CONFIG_BLOCK_END,
    ]

    with open(path, "w", encoding="utf-8") as config_file:
        config_file.write("\n".join([*kept, *block]) + "\n")
    os.chmod(path, 0o600)


def _add_known_hosts(remote_scp: RemoteScpService, path: str, hosts: list[str]) -> None:
    known_hosts = paramiko.HostKeys()
    if os.path.exists(path):
        known_hosts.load(path)

    missing = [host for host in hosts if known_hosts.lookup(host) is None]
    if not missing:
        return

    entries: list[str] = []
    for host in missing:
        ssh = remote_scp.connect(host)
        try:
            key = ssh.get_transport().get_remote_server_key()
            entries.append(f"{host} {key.get_name()} {key.get_base64()}\n")
        finally:
            ssh.close()

    with open(path, "a", encoding="utf-8") as known_hosts_file:
        known_hosts_file.writelines(entries)
    os.chmod(path, 0o600)
