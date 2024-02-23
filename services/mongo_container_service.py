from services.container_service import Container, ContainerService
from config import MONGODB_IMAGE_NAME, MONGODB_IMAGE_VERSION


class MongoContainerService(ContainerService):
    def __init__(self, mongodb_container_name) -> None:
        container = Container(
            mongodb_container_name,
            MONGODB_IMAGE_NAME,
            MONGODB_IMAGE_VERSION,
        )

        super().__init__(container)

    def start_container(self, port: int, username: str, password: str):
        container_id = self._start_container(
            detach=True,
            restart_policy={
                "Name": "on-failure",
                "MaximumRetryCount": 5,
            },
            ports={
                "27017/tcp": port,
            },
            environment={
                "MONGO_INITDB_ROOT_USERNAME": username,
                "MONGO_INITDB_ROOT_PASSWORD": password,
            },
        )

        return container_id
