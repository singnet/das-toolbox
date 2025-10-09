import os
from typing import Dict

import docker

from common import Container, ContainerManager
from common.docker.exceptions import DockerContainerNotFoundError, DockerError
from settings.config import MORK_LOADER_IMAGE_NAME, MORK_LOADER_IMAGE_VERSION


class MorkLoaderContainerManager(ContainerManager):
    def __init__(
        self,
        mork_loader_container_name: str,
        options: Dict = {},
    ) -> None:
        container = Container(
            mork_loader_container_name,
            metadata={
                "port": options.get("mork_loader_port"),
                "image": {
                    "name": MORK_LOADER_IMAGE_NAME,
                    "version": MORK_LOADER_IMAGE_VERSION,
                },
            },
        )

        super().__init__(container)
        self._options = options

    def start_container(self, port: int, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(f"The specified file path '{path}' does not exist.")

        if not os.path.isfile(path):
            raise IsADirectoryError(f"The specified path '{path}' is a directory.")

        try:
            self.stop()
        except (DockerContainerNotFoundError, DockerError):
            pass

        try:
            # filename = os.path.basename(path)
            exec_command = "--file /app/file.metta"

            container = self._start_container(
                environment={},
                command=exec_command,
                volumes={
                    path: {
                        "bind": f"/app/file.metta",
                        "mode": "rw",
                    },
                },
                ports={
                    f"{port}/tcp": port,
                },
                stdin_open=True,
                tty=True,
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
