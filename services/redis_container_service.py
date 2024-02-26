from services.container_service import Container, ContainerService
from config import REDIS_IMAGE_NAME, REDIS_IMAGE_VERSION


class RedisContainerService(ContainerService):
    def __init__(self, redis_container_name) -> None:
        container = Container(
            redis_container_name,
            REDIS_IMAGE_NAME,
            REDIS_IMAGE_VERSION,
        )

        super().__init__(container)

    def start_container(self, port: int):
        container_id = self._start_container(
            detach=True,
            restart_policy={
                "Name": "on-failure",
                "MaximumRetryCount": 5,
            },
            ports={
                "6379/tcp": port,
            },
        )

        return container_id
