import os
from typing import Dict

import docker

from common import Container, ContainerManager
from common.docker.exceptions import DockerContainerNotFoundError, DockerError
from settings.config import METTA_PARSER_IMAGE_NAME, METTA_PARSER_IMAGE_VERSION


class MettaLoaderContainerManager(ContainerManager):
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
                    "name": METTA_PARSER_IMAGE_NAME,
                    "version": METTA_PARSER_IMAGE_VERSION,
                },
            },
        )

        super().__init__(container)
        self._options = options

    def start_container(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"The specified file path '{path}' does not exist.")

        if not os.path.isfile(path):
            raise IsADirectoryError(f"The specified path '{path}' is a directory.")

        try:
            self.stop()
        except (DockerContainerNotFoundError, DockerError):
            pass

        try:
            filename = os.path.basename(path)
            exec_command = f"db_loader {filename}"

            container = self._start_container(
                network_mode="host",
                environment={
                    "DAS_REDIS_HOSTNAME": self._options.get('redis_hostname'),
                    "DAS_REDIS_PORT": self._options.get('redis_port'),
                    "DAS_MONGODB_HOSTNAME": self._options.get('mongodb_hostname'),
                    "DAS_MONGODB_PORT": self._options.get('mongodb_port'),
                    "DAS_MONGODB_USERNAME": self._options.get('mongodb_username'),
                    "DAS_MONGODB_PASSWORD": self._options.get('mongodb_password'),
                },
                command=exec_command,
                volumes={
                    path: {
                        "bind": f"/tmp/{filename}",
                        "mode": "rw",
                    },
                },
                stdin_open=True,
                tty=True,
                auto_remove=True,
                remove=True,
            )

            self.logs()

            exit_code = self.get_container_exit_status(container)

            if exit_code != 0:
                raise DockerError(f"File '{os.path.basename(path)}' could not be loaded.")

            return None
        except docker.errors.APIError as e:
            raise DockerError(e.explanation)
