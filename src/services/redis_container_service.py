import docker
from services.container_service import Container, ContainerService
from config import REDIS_IMAGE_NAME, REDIS_IMAGE_VERSION
from exceptions import ContainerAlreadyRunningException, DockerException
from typing import AnyStr, Union


class RedisContainerService(ContainerService):
    def __init__(
        self,
        redis_container_name,
        exec_context: Union[AnyStr, None] = None,
    ) -> None:
        container = Container(
            redis_container_name,
            REDIS_IMAGE_NAME,
            REDIS_IMAGE_VERSION,
        )

        super().__init__(container, exec_context)

    def start_container(
        self,
        port: int,
    ):
        if self.get_container().is_running():
            raise ContainerAlreadyRunningException()

        try:
            command_params = [
                "redis-server",
                "--port",
                f"{port}",
                "--cluster-enabled",
                "yes",
                "--cluster-config-file",
                "nodes.conf",
                "--cluster-node-timeout",
                "5000",
                "--appendonly",
                "yes",
                "--protected-mode",
                "no",
            ]

            container_id = self._start_container(
                restart_policy={
                    "Name": "on-failure",
                    "MaximumRetryCount": 5,
                },
                command=command_params,
                network_mode="host",
            )

            return container_id
        except docker.errors.APIError as e:
            # print(e.explanation) # TODO: ADD TO LOGGING FILE

            raise DockerException(e.explanation)
