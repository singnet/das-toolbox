import os
from typing import Dict

import docker

from common import Container, ContainerManager
from common.docker.exceptions import DockerContainerNotFoundError, DockerError
from settings.config import DAS_MORK_LOADER_IMAGE_NAME, DAS_MORK_LOADER_IMAGE_VERSION


class MettaMorkLoaderContainerManager(ContainerManager):
    def __init__(
        self,
        mork_loader_container_name: str,
        options: Dict = {},
    ) -> None:
        container = Container(
            mork_loader_container_name,
            metadata={
                "port": None,
                "image": {
                    "name": DAS_MORK_LOADER_IMAGE_NAME,
                    "version": DAS_MORK_LOADER_IMAGE_VERSION,
                },
            },
        )

        super().__init__(container)
        self._options = options

    def _gen_mork_metta_loader_command(self, filename: str) -> str:
        exec_command = f"--file {filename}".strip()

        return exec_command

    def start_container(self, path):
        try:
            self.stop()
        except (DockerContainerNotFoundError, DockerError):
            pass

        try:
            filename = os.path.basename(path)
            file_container_path = f"/tmp/mork/{filename}"

            exec_command = self._gen_mork_metta_loader_command(file_container_path)
            container = self._start_container(
                command=exec_command,
                volumes={
                    path: {
                        "bind": file_container_path,
                        "mode": "rw",
                    },
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
