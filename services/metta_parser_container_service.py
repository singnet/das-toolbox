import os
import subprocess
from exceptions import ValidateFailed
from services.container_service import Container, ContainerService
from config import METTA_PARSER_IMAGE_NAME, METTA_PARSER_IMAGE_VERSION


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

        docker_command = f"docker run --rm --name {self.get_container().get_name()} -i -v {os.path.dirname(filepath)}:/tmp {self.get_container().get_image()} syntax_check {os.path.basename(filepath)}"
        exit_code = subprocess.call(
            docker_command,
            shell=True,
            text=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        if exit_code > 0:
            raise ValidateFailed()

        return None
