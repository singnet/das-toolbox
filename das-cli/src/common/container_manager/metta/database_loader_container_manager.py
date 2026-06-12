import os
from typing import Dict

import docker

from common import Container, ContainerManager
from common.docker.exceptions import DockerContainerNotFoundError, DockerError
from settings.config import DAS_IMAGE_NAME, DAS_IMAGE_VERSION, CURRENT_CONFIGFILE_PATH

class DatabaseLoaderContainerManager(ContainerManager):
    def __init__(
        self,
        loader_container_name: str,
        options: Dict = {},
    ) -> None:
        container = Container(
            loader_container_name,
            metadata={
                "port": None,
                "image": {
                    "name": DAS_IMAGE_NAME,
                    "version": DAS_IMAGE_VERSION,
                },
            },
        )

        super().__init__(container)
        self._options = options

    def start_container(self, path):

        try:
            self.stop()
        except (DockerContainerNotFoundError, DockerError):
            pass

        try:

            print(path)

            user_config_path = CURRENT_CONFIGFILE_PATH
            exec_command = self._gen_metta_loader_command(user_config_path=user_config_path, filepath=path)

            container = self._start_container(
                command=exec_command,
                volumes={
                    path: {
                        "bind": path,
                        "mode": "rw",
                    },
                    user_config_path: {
                        "bind": user_config_path,
                        "mode": "ro"
                    }
                },
                stdin_open=True,
                tty=False,
                auto_remove=False,
            )

            self.logs()

            exit_code = self.get_container_exit_status(container)
            container.remove(v=True, force=True)

            if exit_code != 0:
                raise DockerError(f"File '{os.path.basename(path)}' could not be loaded.")

            return None
        except docker.errors.APIError as e:
            raise DockerError(e.explanation)

    def _gen_metta_loader_command(self, user_config_path: str, filepath: str) -> str:
        exec_command = f"db_loader --config={user_config_path} --file={filepath}".strip()

        print(exec_command)

        return exec_command