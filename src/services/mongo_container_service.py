import docker
from services.container_service import Container, ContainerService
from config import MONGODB_IMAGE_NAME, MONGODB_IMAGE_VERSION
from exceptions import ContainerAlreadyRunningException, DockerException


class MongoContainerService(ContainerService):
    def __init__(self, mongodb_container_name) -> None:
        container = Container(
            mongodb_container_name,
            MONGODB_IMAGE_NAME,
            MONGODB_IMAGE_VERSION,
        )

        super().__init__(container)

    def start_container(
        self,
        port: int,
        username: str,
        password: str,
    ):
        if self.is_running():
            raise ContainerAlreadyRunningException()

        try:
            container_id = self._start_container(
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
        except docker.errors.APIError as e:
            # print(e.explanation) # TODO: ADD TO LOGGING FILE

            raise DockerException(e.explanation)
