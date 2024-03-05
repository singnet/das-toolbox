import os
import subprocess
from exceptions import ValidateFailed
from services.container_service import Container, ContainerService
from config import (
    METTA_LOADER_IMAGE_NAME,
    METTA_LOADER_IMAGE_VERSION,
)


class MettaLoaderContainerService(ContainerService):
    def __init__(
        self,
        loader_container_name,
        redis_container_name,
        mongodb_container_name,
    ) -> None:
        container = Container(
            loader_container_name,
            METTA_LOADER_IMAGE_NAME,
            METTA_LOADER_IMAGE_VERSION,
        )
        self.redis_container = Container(redis_container_name)
        self.mongodb_container = Container(mongodb_container_name)

        super().__init__(container)

    def start_container(
        self,
        filepath,
        mongodb_port,
        mongodb_username,
        mongodb_password,
        redis_port,
    ):
        if not os.path.exists(filepath):
            raise FileNotFoundError()

        if not os.path.isfile(filepath):
            raise IsADirectoryError()

        docker_command = f"docker run --rm --net host --name {self.get_container().get_name()} -e DAS_REDIS_HOSTNAME=localhost -e DAS_REDIS_PORT={redis_port} -e DAS_MONGODB_HOSTNAME=localhost -e DAS_MONGODB_PORT={mongodb_port} -e DAS_MONGODB_USERNAME={mongodb_username} -e DAS_MONGODB_PASSWORD={mongodb_password} -i -v {os.path.dirname(filepath)}:/tmp {self.get_container().get_image()} db_loader {os.path.basename(filepath)}"
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
