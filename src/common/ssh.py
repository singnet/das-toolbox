import paramiko
from typing import Union


class SSHConnection:
    def __init__(self, ssh_host, ssh_port, ssh_username, ssh_password):
        self.ssh_host = ssh_host
        self.ssh_port = ssh_port
        self.ssh_username = ssh_username
        self.ssh_password = ssh_password
        self.ssh = None
        self.sftp = None

    def __enter__(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(
            self.ssh_host,
            port=self.ssh_port,
            username=self.ssh_username,
            password=self.ssh_password,
        )
        self.sftp = self.ssh.open_sftp()
        return self.ssh, self.sftp

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.sftp:
            self.sftp.close()
        if self.ssh:
            self.ssh.close()


def open(
    host: str,
    username: str,
    password: Union[str, None] = None,
    port: int = 22,
):
    return SSHConnection(host, port, username, password)
