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

        # Require a known host key; add targets to known_hosts before remote transfer.
        ssh.set_missing_host_key_policy(RejectPolicy())

        return ssh

    def _exec_checked(self, ssh: SSHClient, command: str, *, failure_message: str) -> str:
        _stdin, stdout, stderr = ssh.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()
        output = stdout.read().decode().strip()
        error_output = stderr.read().decode().strip()

        if exit_status != 0:
            detail = error_output or output or f"exit status {exit_status}"
            raise RemoteSshTransferError(failure_message, detail=detail)

        return output

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
        home = self._exec_checked(
            ssh,
            "echo $HOME",
            failure_message="Failed to resolve remote home directory.",
        )
        if not home:
            raise RemoteSshTransferError(
                "Failed to resolve remote home directory.",
                detail="Remote $HOME was empty.",
            )
        return home

    def ensure_remote_dir(self, ssh: SSHClient, remote_dir: str) -> None:
        self._exec_checked(
            ssh,
            f"mkdir -p {shlex.quote(remote_dir)}",
            failure_message=f"Failed to create remote directory {remote_dir}.",
        )

    def remote_file_exists(self, ssh: SSHClient, file_path: str) -> bool:
        _stdin, stdout, stderr = ssh.exec_command(
            f"test -f {shlex.quote(file_path)} && echo exists"
        )
        exit_status = stdout.channel.recv_exit_status()
        if exit_status not in (0, 1):
            error_output = stderr.read().decode().strip()
            raise RemoteSshTransferError(
                f"Failed to check remote file {file_path}.",
                detail=error_output or f"exit status {exit_status}",
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
