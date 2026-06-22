import os
from io import BytesIO

from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient

from shared.internal.constants import DEFAULT_SSHKEY_CLONE_PATH
from shared.internal.web_configuration import WebConfiguration


class RemoteScpService:

    def __init__(self, web_config: WebConfiguration):
        self.web_config = web_config

    def ensure_profile(self) -> tuple[str, str]:
        profile = self.web_config.user_profile
        username = profile.get("profile_username", "root")
        key_path = profile.get("profile_ssh_keypath") or DEFAULT_SSHKEY_CLONE_PATH

        if not os.path.exists(key_path):
            raise ValueError("SSH key is not configured. Set up your profile first.")

        return username, key_path

    def connect(self, host: str) -> SSHClient:
        username, key_path = self.ensure_profile()

        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(hostname=host, username=username, key_filename=key_path)

        return ssh

    def get_remote_home(self, ssh: SSHClient) -> str:
        stdin, stdout, stderr = ssh.exec_command("echo $HOME")
        return stdout.read().decode().strip()

    def remote_file_exists(self, ssh: SSHClient, file_path: str) -> bool:
        stdin, stdout, stderr = ssh.exec_command(
            f"test -f {file_path} && echo exists"
        )
        return stdout.read().decode().strip() == "exists"

    def transfer_fileobj(
        self,
        host: str,
        file_obj,
        remote_path: str,
        *,
        remote_dir: str | None = None,
    ) -> str:
        ssh = self.connect(host)

        try:
            if remote_dir:
                ssh.exec_command(f"mkdir -p {remote_dir}")

            with SCPClient(ssh.get_transport()) as scp:
                scp.putfo(file_obj, remote_path=remote_path)

            return remote_path
        finally:
            ssh.close()

    def transfer_bytes(
        self,
        host: str,
        content: bytes,
        remote_path: str,
        *,
        remote_dir: str | None = None,
    ) -> str:
        return self.transfer_fileobj(
            host,
            BytesIO(content),
            remote_path,
            remote_dir=remote_dir,
        )
