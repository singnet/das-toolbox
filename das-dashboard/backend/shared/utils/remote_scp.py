import os
import shlex
from io import BytesIO

from paramiko import RejectPolicy, SSHClient
from paramiko.ssh_exception import AuthenticationException, NoValidConnectionsError, SSHException
from scp import SCPClient, SCPException

from shared.exceptions.custom_exceptions import RemoteSshConnectionError, RemoteSshTransferError
from shared.internal.constants import DEFAULT_SSHKEY_CLONE_PATH
from shared.internal.web_configuration import WebConfiguration

SSH_CONNECT_TIMEOUT = 30


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

    def _prepare_ssh_client(self) -> SSHClient:
        ssh = SSHClient()
        ssh.load_system_host_keys()

        user_known_hosts = os.path.expanduser("~/.ssh/known_hosts")
        if os.path.exists(user_known_hosts):
            ssh.load_host_keys(user_known_hosts)

        # Require a known host key; add targets to known_hosts before exporting.
        ssh.set_missing_host_key_policy(RejectPolicy())

        return ssh

    def connect(self, host: str) -> SSHClient:
        username, key_path = self.ensure_profile()
        ssh = self._prepare_ssh_client()

        try:
            ssh.connect(
                hostname=host,
                username=username,
                key_filename=key_path,
                timeout=SSH_CONNECT_TIMEOUT,
            )
        except NoValidConnectionsError as error:
            raise RemoteSshConnectionError(
                f"Could not connect to {host}.",
                detail=str(error),
            ) from error
        except AuthenticationException as error:
            raise RemoteSshConnectionError(
                f"SSH authentication failed for {host}.",
                detail=str(error),
            ) from error
        except SSHException as error:
            raise RemoteSshConnectionError(
                f"SSH connection failed for {host}.",
                detail=str(error),
            ) from error
        except OSError as error:
            raise RemoteSshConnectionError(
                f"SSH connection failed for {host}.",
                detail=str(error),
            ) from error

        return ssh

    def get_remote_home(self, ssh: SSHClient) -> str:
        stdin, stdout, stderr = ssh.exec_command("echo $HOME")
        return stdout.read().decode().strip()

    def ensure_remote_dir(self, ssh: SSHClient, remote_dir: str) -> None:
        ssh.exec_command(f"mkdir -p {shlex.quote(remote_dir)}")

    def remote_file_exists(self, ssh: SSHClient, file_path: str) -> bool:
        stdin, stdout, stderr = ssh.exec_command(
            f"test -f {shlex.quote(file_path)} && echo exists"
        )
        return stdout.read().decode().strip() == "exists"

    def transfer_fileobj(
        self,
        host: str,
        file_obj,
        remote_path: str,
        *,
        remote_dir: str | None = None,
        ssh: SSHClient | None = None,
    ) -> str:
        own_ssh = ssh is None
        if own_ssh:
            ssh = self.connect(host)

        try:
            if remote_dir:
                self.ensure_remote_dir(ssh, remote_dir)

            try:
                with SCPClient(ssh.get_transport()) as scp:
                    scp.putfo(file_obj, remote_path=remote_path)
            except SCPException as error:
                raise RemoteSshTransferError(
                    f"Failed to transfer file to {host}.",
                    detail=str(error),
                ) from error

            return remote_path
        finally:
            if own_ssh:
                ssh.close()

    def transfer_bytes(
        self,
        host: str,
        content: bytes,
        remote_path: str,
        *,
        remote_dir: str | None = None,
        ssh: SSHClient | None = None,
    ) -> str:
        return self.transfer_fileobj(
            host,
            BytesIO(content),
            remote_path,
            remote_dir=remote_dir,
            ssh=ssh,
        )
