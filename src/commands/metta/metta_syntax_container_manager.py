import os
import docker
import docker.errors
from common import Container, ContainerManager
from common.docker.exceptions import DockerContainerNotFoundError, DockerError
from config import (
    METTA_PARSER_IMAGE_NAME,
    METTA_PARSER_IMAGE_VERSION,
)


class MettaSyntaxContainerManager(ContainerManager):
    def __init__(self) -> None:
        container = Container(
            "das-metta-parser",
            METTA_PARSER_IMAGE_NAME,
            METTA_PARSER_IMAGE_VERSION,
        )
        super().__init__(container)

    def start_container(self, filepath):
        if not os.path.exists(filepath):
            raise FileNotFoundError()

        if not os.path.isfile(filepath):
            raise IsADirectoryError()

        try:
            self.stop()
        except (DockerContainerNotFoundError, DockerError):
            pass

        try:
            filename = os.path.basename(filepath)
            exec_command = f"syntax_check {filename}"

            container = self._start_container(
                command=exec_command,
                volumes={
                    filepath: {
                        "bind": f"/tmp/{filename}",
                        "mode": "rw",
                    },
                },
                stdin_open=True,
                tty=True,
            )

            self.logs()

            exit_code = self.container_status(container)

            if exit_code != 0:
                raise DockerError()

        except docker.errors.APIError as e:
            raise DockerError(e.explanation)

        return None
