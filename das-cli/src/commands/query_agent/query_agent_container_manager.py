from typing import Dict

import docker

from common import Container, ContainerImageMetadata, ContainerManager
from common.docker.exceptions import DockerContainerNotFoundError, DockerError
from settings.config import QUERY_AGENT_IMAGE_NAME, QUERY_AGENT_IMAGE_VERSION


class QueryAgentContainerManager(ContainerManager):
    def __init__(
        self,
        query_agent_container_name: str,
        options: Dict = {},
    ) -> None:
        container = Container(
            query_agent_container_name,
            metadata={
                "port": options.get("query_agent_port"),
                "image": ContainerImageMetadata(
                    {
                        "name": QUERY_AGENT_IMAGE_NAME,
                        "version": QUERY_AGENT_IMAGE_VERSION,
                    }
                ),
            },
        )
        self._options = options

        super().__init__(container)

    def _gen_query_agent_command(self, port_range: str) -> str:
        query_agent_port = int(self._options.get("query_agent_port", 0))

        return f"{query_agent_port} {port_range}"

    def start_container(self, port_range: str):
        self.raise_running_container()
        self.raise_on_port_in_use([int(self._options.get("query_agent_port", 0))])

        try:
            self.stop()
        except (DockerContainerNotFoundError, DockerError):
            pass

        try:
            exec_command = self._gen_query_agent_command(port_range)

            container_id = self._start_container(
                network_mode="host",
                restart_policy={
                    "Name": "on-failure",
                    "MaximumRetryCount": 5,
                },
                environment={
                    "DAS_MONGODB_HOSTNAME": self._options.get("mongodb_hostname"),
                    "DAS_MONGODB_PORT": self._options.get("mongodb_port"),
                    "DAS_MONGODB_USERNAME": self._options.get("mongodb_username"),
                    "DAS_MONGODB_PASSWORD": self._options.get("mongodb_password"),
                    "DAS_REDIS_HOSTNAME": self._options.get("mongodb_hostname"),
                    "DAS_REDIS_PORT": self._options.get("redis_port"),
                    "DAS_ATTENTION_BROKER_ADDRESS": self._options.get("attention_broker_hostname"),
                    "DAS_ATTENTION_BROKER_PORT": self._options.get("attention_broker_port"),
                },
                command=exec_command,
            )

            return container_id
        except docker.errors.APIError as e:
            if e.response.reason == "Not Found":
                raise DockerContainerNotFoundError(
                    f"The docker image {self.get_container().image} for the quey agent could not be found!"
                )

            raise DockerError(e.explanation)
