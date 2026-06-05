import json
import os
import subprocess
from fastapi import UploadFile
from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient

from shared.internal.web_configuration import WebConfiguration
from shared.internal.constants import (
    DEFAULT_METTA_FILES_PATH, 
    REMOTE_METTA_FILES_PATH, 
    DEFAULT_SSHKEY_CLONE_PATH
)
from shared.exceptions.custom_exceptions import (
    FileSaveException, 
    FileAlreadyExistsException,
    DasCliCommandException
)

LOCAL_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0"}


class DatabaseServices:
    
    def __init__(self, web_configuration: WebConfiguration):
        self.web_config = web_configuration

    def _get_remote_home(self, ssh: SSHClient) -> str:
        stdin, stdout, stderr = ssh.exec_command("echo $HOME")
        return stdout.read().decode().strip()

    def _remote_file_exists(self, ssh: SSHClient, file_path: str) -> bool:
        stdin, stdout, stderr = ssh.exec_command(
            f"test -f {file_path} && echo exists"
        )
        return stdout.read().decode().strip() == "exists"

    def _transfer_file_scp(self, host: str, file: UploadFile, force_overwrite: bool) -> str:
        profile = self.web_config.user_profile
        ssh_username = profile.get("profile_username", "root")
        ssh_key = profile.get("profile_ssh_keypath") or DEFAULT_SSHKEY_CLONE_PATH

        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(hostname=host, username=ssh_username, key_filename=ssh_key)
        
        try:
            home = self._get_remote_home(ssh)
            remote_save_path = f"{home}{REMOTE_METTA_FILES_PATH}/{file.filename}"

            ssh.exec_command(f"mkdir -p {home}{REMOTE_METTA_FILES_PATH}")

            if self._remote_file_exists(ssh, remote_save_path) and not force_overwrite:
                raise FileAlreadyExistsException(
                    message="The uploaded file already exists in the user's machine.", 
                    file_path=remote_save_path
                )

            with SCPClient(ssh.get_transport()) as scp:
                scp.putfo(file.file, remote_path=remote_save_path)
            
            return remote_save_path
        finally:
            ssh.close()

    async def save_metta_file(self, host: str, knowledge_file: UploadFile, force_overwrite: bool) -> str:
        file_name = knowledge_file.filename
        file_path = f"{DEFAULT_METTA_FILES_PATH}/{file_name}"
        file_exists = os.path.exists(file_path)

        if file_exists and not force_overwrite:
            raise FileAlreadyExistsException(
                message="The uploaded file already exists in the user's machine.", 
                file_path=file_path
            )

        if host not in LOCAL_HOSTS:
            return self._transfer_file_scp(
                host=host, 
                file=knowledge_file, 
                force_overwrite=force_overwrite
            )
        
        os.makedirs(DEFAULT_METTA_FILES_PATH, exist_ok=True)
        with open(file_path, "wb") as local_api_copy:
            local_api_copy.write(await knowledge_file.read()) 

        return file_path
            
    def load_metta_file_into_db(self, host: str, metta_file_path: str):
        cmd = ["das-cli", "metta", "load", metta_file_path]

        if host not in LOCAL_HOSTS:
            profile = self.web_config.user_profile
            ssh_username = profile.get("profile_username", "root")
            ssh_key = profile.get("profile_ssh_keypath") or DEFAULT_SSHKEY_CLONE_PATH
            cmd.extend(["--remote", "-h", host, "-u", ssh_username, "-k", ssh_key])

        cmd.extend(["-o", "json"])

        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True,
                check=True
            )
            
            stdout_content = result.stdout
            try:
                stdout_content = json.loads(result.stdout)
            except Exception:
                stdout_content = result.stdout.replace("\n", "").strip()

            return stdout_content

        except subprocess.CalledProcessError as e:
            error_output = (e.stderr or e.stdout or "Unknown Subprocess Error").strip()
            raise DasCliCommandException(error_output)
        except Exception as e:
            raise DasCliCommandException(str(e))