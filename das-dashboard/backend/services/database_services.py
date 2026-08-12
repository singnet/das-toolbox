import os
from fastapi import UploadFile
from scp import SCPClient, SCPException

from shared.internal.web_configuration import WebConfiguration
from shared.internal.constants import (
    DEFAULT_METTA_FILES_PATH,
    DEFAULT_SSHKEY_CLONE_PATH,
    LOCAL_HOSTS,
    REMOTE_METTA_FILES_PATH,
)
from shared.exceptions.custom_exceptions import (
    FileAlreadyExistsException,
    RemoteSshTransferError,
)
from shared.utils.remote_scp import RemoteScpService
from shared.utils.upload_utils import safe_upload_filename
from shared.utils.das_cli_response import run_das_cli_json_command


class DatabaseServices:

    def __init__(self, web_configuration: WebConfiguration):
        self.web_config = web_configuration
        self.remote_scp = RemoteScpService(web_configuration)

    def _transfer_file_scp(self, host: str, file: UploadFile, force_overwrite: bool) -> str:
        ssh = self.remote_scp.connect(host)

        try:
            home = self.remote_scp.get_remote_home(ssh)
            remote_dir = f"{home}{REMOTE_METTA_FILES_PATH}"
            file_name = safe_upload_filename(file.filename)
            remote_save_path = f"{remote_dir}/{file_name}"

            self.remote_scp.ensure_remote_dir(ssh, remote_dir)

            if self.remote_scp.remote_file_exists(ssh, remote_save_path) and not force_overwrite:
                raise FileAlreadyExistsException(
                    message="The uploaded file already exists in the user's machine.",
                    file_path=remote_save_path,
                )

            try:
                with SCPClient(ssh.get_transport()) as scp:
                    scp.putfo(file.file, remote_path=remote_save_path)
            except SCPException as error:
                raise RemoteSshTransferError(
                    f"Failed to transfer file to {host}.",
                    detail=str(error),
                ) from error

            return remote_save_path
        finally:
            ssh.close()

    async def save_metta_file(self, host: str, knowledge_file: UploadFile, force_overwrite: bool) -> str:
        file_name = safe_upload_filename(knowledge_file.filename)
        file_path = f"{DEFAULT_METTA_FILES_PATH}/{file_name}"
        file_exists = os.path.exists(file_path)

        if file_exists and not force_overwrite:
            raise FileAlreadyExistsException(
                message="The uploaded file already exists in the user's machine.",
                file_path=file_path,
            )

        if host not in LOCAL_HOSTS:
            return self._transfer_file_scp(
                host=host,
                file=knowledge_file,
                force_overwrite=force_overwrite,
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

        return run_das_cli_json_command(
            cmd,
            default_message="The das-cli metta load command failed.",
        )
