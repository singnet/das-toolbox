import docker
import socket
from common import Container, ContainerManager
from config import OPENFAAS_IMAGE_NAME
from common.docker.exceptions import (
    DockerError,
    DockerContainerNotFoundError,
)


class OpenFaaSContainerManager(ContainerManager):
    def __init__(self, openfaas_container_name) -> None:
        container = Container(openfaas_container_name, OPENFAAS_IMAGE_NAME)
        super().__init__(container)

    def is_port_in_use(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("localhost", port)) == 0

    def start_container(
        self,
        function_version: str,
        redis_port: int,
        mongodb_port: int,
        mongodb_username: str,
        mongodb_password: str,
    ):
        self.get_container().set_image_version(function_version)

        try:
            self.stop()
        except (DockerContainerNotFoundError, DockerError):
            pass

        if self.is_port_in_use(
            8080
        ):  # TODO: This check is only required for host network mode (remove it when change it)
            raise DockerError(
                "Port 8080 is already in use. Please stop the service that is currently using this port."
            )

        try:
            container_id = self._start_container(
                network_mode="host",
                restart_policy={
                    "Name": "on-failure",
                    "MaximumRetryCount": 5,
                },
                environment={
                    "exec_timeout": "30m",
                    "service_timeout": "30m",
                    "ack_wait": "30m",
                    "read_timeout": "30m",
                    "write_timeout": "30m",
                    "exec_timeout": "30m",
                    "DAS_MONGODB_HOSTNAME": "localhost",
                    "DAS_REDIS_HOSTNAME": "localhost",
                    "DAS_MONGODB_NAME": "das",
                    "DAS_MONGODB_PASSWORD": mongodb_password,
                    "DAS_MONGODB_PORT": mongodb_port,
                    "DAS_MONGODB_USERNAME": mongodb_username,
                    "DAS_REDIS_PORT": redis_port,
                },
            )

            return container_id
        except docker.errors.APIError as e:
            if e.response.reason == "Not Found":
                raise DockerContainerNotFoundError(
                    f"The image {self.get_container().get_image()} for the function was not found in the Docker Hub repository. Please verify the existence of the version or ensure the correct function name is used."
                )

            raise DockerError(e.explanation)
