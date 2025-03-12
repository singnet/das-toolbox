from typing import Dict

import docker

from common import Container, ContainerImageMetadata, ContainerManager
from common.docker.exceptions import DockerContainerNotFoundError, DockerError
from settings.config import ATTENTION_BROKER_IMAGE_NAME, ATTENTION_BROKER_IMAGE_VERSION


class AttentionBrokerManager(ContainerManager):
    def __init__(
        self,
        attention_broker_container_name: str,
        options: Dict = {},
    ) -> None:
        container = Container(
            attention_broker_container_name,
            metadata={
                "port": options.get("attention_broker_port"),
                "image": ContainerImageMetadata(
                    {
                        "name": ATTENTION_BROKER_IMAGE_NAME,
                        "version": ATTENTION_BROKER_IMAGE_VERSION,
                    }
                ),
            },
        )
        self._options = options

        super().__init__(container)

    def start_container(self):
        try:
            self.stop()
        except (DockerContainerNotFoundError, DockerError):
            pass

        try:
            container_id = self._start_container(
                restart_policy={
                    "Name": "on-failure",
                    "MaximumRetryCount": 5,
                },
                environment={
                    "DAS_MONGODB_HOSTNAME": self._options.get('mongodb_hostname'),
                    "DAS_REDIS_HOSTNAME": self._options.get('redis_hostname'),
                    "DAS_MONGODB_NAME": self._options.get('mongodb_name'),
                    "DAS_MONGODB_PASSWORD": self._options.get('mongodb_password'),
                    "DAS_MONGODB_PORT": self._options.get('mongodb_port'),
                    "DAS_MONGODB_USERNAME": self._options.get('mongodb_username'),
                    "DAS_REDIS_PORT": self._options.get('redis_port'),
                    "DAS_ATTENTION_BROKER_PORT": self._options.get('attention_broker_port')
                },
            )

            return container_id
        except docker.errors.APIError as e:
            if e.response.reason == "Not Found":
                raise DockerContainerNotFoundError(
                    f"The docker image {self.get_container().image} for the attention broker could not be found!"
                )

            raise DockerError(e.explanation)
