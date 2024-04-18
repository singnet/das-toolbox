import os
import docker
from exceptions import NotFound, DockerException, MettaLoadException
from services.container_service import Container, ContainerService
from config import (
    METTA_PARSER_IMAGE_NAME,
    METTA_PARSER_IMAGE_VERSION,
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
            METTA_PARSER_IMAGE_NAME,
            METTA_PARSER_IMAGE_VERSION,
        )
        self.redis_container = Container(redis_container_name)
        self.mongodb_container = Container(mongodb_container_name)

        super().__init__(container)

    def start_container(
        self,
        path,
        mongodb_port,
        mongodb_username,
        mongodb_password,
        redis_port,
    ):

        if not os.path.exists(path):
            raise FileNotFoundError(f"The specified file path '{path}' does not exist.")

        if not os.path.isfile(path):
            raise IsADirectoryError(f"The specified path '{path}' is a directory.")

        try:
            self.stop()
        except (NotFound, DockerException):
            pass

        try:
            log_path = "/tmp/logs.log"
            filename = os.path.basename(path)
            exec_command = (
                f'sh -c "stdbuf -o0 -e0 db_loader {filename} > {log_path} 2>&1"'
            )

            container = self._start_container(
                network_mode="host",
                environment={
                    "DAS_REDIS_HOSTNAME": "localhost",
                    "DAS_REDIS_PORT": str(redis_port),
                    "DAS_MONGODB_HOSTNAME": "localhost",
                    "DAS_MONGODB_PORT": str(mongodb_port),
                    "DAS_MONGODB_USERNAME": mongodb_username,
                    "DAS_MONGODB_PASSWORD": mongodb_password,
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
            )

            self.tail(log_path)

            exit_code = self.container_status(container)

            if exit_code != 0:
                raise MettaLoadException(
                    f"File '{os.path.basename(path)}' could not be loaded. Use the command `metta check {path}` to ensure this is a valid file."
                )

            return None
        except docker.errors.APIError as e:
            # print(e.explanation) # TODO: ADD TO LOGGING FILE

            raise DockerException(e.explanation)
