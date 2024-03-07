import os
import docker
from services.container_service import Container, ContainerService
from config import METTA_PARSER_IMAGE_NAME, METTA_PARSER_IMAGE_VERSION
from exceptions import NotFound, DockerException, MettaSyntaxException


class MettaParserContainerService(ContainerService):
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
        except (NotFound, DockerException):
            pass

        try:
            self._start_container(
                command=f"syntax_check {os.path.basename(filepath)}",
                volumes={os.path.dirname(filepath): {"bind": "/tmp", "mode": "rw"}},
                remove=True,
                stdin_open=True,
                tty=True,
            )
        except docker.errors.APIError as e:
            # print(e.explanation) # TODO: ADD TO LOGGING FILE

            raise DockerException(e.explanation)
        except docker.errors.ContainerError as e:
            # print(e.explanation) # TODO: ADD TO LOGGING FILE

            raise MettaSyntaxException()

        return None
