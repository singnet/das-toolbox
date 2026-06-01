from fastapi import UploadFile
from shared.internal.constants import DEFAULT_METTA_FILES_PATH, REMOTE_METTA_FILES_PATH
from shared.exceptions.custom_exceptions import FileSaveException, FileAlreadyExistsException
from shared.internal.web_configuration import WebConfiguration
from paramiko import SSHClient, AutoAddPolicy
import subprocess
import os
from scp import SCPClient

class DatabaseServices:
    
    def __init__(self, web_configuration):
        self.web_config : WebConfiguration = web_configuration

    def _get_remote_home(self, ssh: SSHClient):
        stdin, stdout, stderr = ssh.exec_command("echo $HOME")
        remote_home = stdout.read().decode().strip()
        return remote_home

    def _remote_file_exists(self, ssh: SSHClient, file_path: str):
        stdin, stdout, stderr = ssh.exec_command(
            f"test -f {file_path} && echo exists"
        )
        return stdout.read().decode().strip() == "exists"

    def _transfer_file_scp(self, host : str, file : UploadFile, force_overwrite: bool):

        ssh_username = self.web_config.user_profile["profile_username"]
        ssh_key = self.web_config.user_profile["profile_ssh_keypath"]

        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(hostname=host, username=ssh_username, key_filename=ssh_key)
        
        home = self._get_remote_home(ssh)
        remote_save_path = f"{home}{REMOTE_METTA_FILES_PATH}{file.filename}"

        ssh.exec_command(f"mkdir -p {home}{REMOTE_METTA_FILES_PATH}")

        if self._remote_file_exists(ssh, remote_save_path) and not force_overwrite:
            ssh.close()
            raise FileAlreadyExistsException(message="The uploaded file already exists in the user's machine.", file_path=remote_save_path)

        with SCPClient(ssh.get_transport()) as scp:
            scp.putfo(file.file, remote_path=remote_save_path)
        
        ssh.close()

        return remote_save_path

    async def save_metta_file(self, host: str, knowledge_file : UploadFile, force_overwrite : bool):

        file_name = knowledge_file.filename
        file_path = f"{DEFAULT_METTA_FILES_PATH}{file_name}"
        file_exists = os.path.exists(file_path)

        if file_exists and not force_overwrite:
            raise FileAlreadyExistsException(message="The uploaded file already exists in the user's machine.", file_path=file_path)

        if host not in ("127.0.0.1", "0.0.0.0", "localhost"):
            remote_path = self._transfer_file_scp(host=host, file=knowledge_file, force_overwrite=force_overwrite)
            return remote_path
        
        else:
            os.makedirs(DEFAULT_METTA_FILES_PATH, exist_ok=True)

            local_api_copy = open(file_path, "wb")
            local_api_copy.write(await knowledge_file.read()) 
            local_api_copy.close()

            return file_path
            

    def load_metta_file_into_db(self, host: str, metta_file_path : str):
        cmd = ["das-cli", "metta", "load", metta_file_path]

        if host not in ("127.0.0.1", "0.0.0.0", "localhost"):

            ssh_username = self.web_config.user_profile["profile_username"]
            ssh_key = self.web_config.user_profile["profile_ssh_keypath"]
            cmd.extend(["--remote", "-h", host, "-u", ssh_username, "-k", ssh_key])

        cmd.extend(["-o", "json"])
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout