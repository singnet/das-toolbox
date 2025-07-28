from typing import Dict

import docker

from common import Container, ContainerImageMetadata, ContainerManager
from common.docker.exceptions import DockerContainerNotFoundError, DockerError
from settings.config import EVOLUTION_BROKER_IMAGE_NAME, EVOLUTION_BROKER_IMAGE_VERSION


class EvolutionBrokerManager(ContainerManager):
    def __init__(
        self,
        evolution_broker_container_name: str,
        options: Dict = {},
    ) -> None:
        container = Container(
            evolution_broker_container_name,
            metadata={
                "port": options.get("evolution_broker_port"),
                "image": ContainerImageMetadata(
                    {
                        "name": EVOLUTION_BROKER_IMAGE_NAME,
                        "version": EVOLUTION_BROKER_IMAGE_VERSION,
                    }
                ),
            },
        )
        self._options = options

        super().__init__(container)

    def _gen_evolution_broker_command(
        self,
        evolution_broker_port: int,
        port_range: str,
    ) -> str:
        query_agent_hostname = str(self._options.get("query_agent_hostname", ""))
        query_agent_port = int(self._options.get("query_agent_port", 0))

        query_agent_address = f"{query_agent_hostname}:{query_agent_port}"

        return f"{evolution_broker_port} {port_range} {query_agent_address}"

    def start_container(self, port_range: str) -> str:
        self.raise_running_container()
        self.raise_on_port_in_use([int(self._options.get("evolution_broker_port", 0))])

        try:
            self.stop()
        except (DockerContainerNotFoundError, DockerError):
            pass

        try:
            evolution_broker_port = int(self._options.get("evolution_broker_port", 0))
            exec_command = self._gen_evolution_broker_command(evolution_broker_port, port_range)

            container_id = self._start_container(
                restart_policy={
                    "Name": "on-failure",
                    "MaximumRetryCount": 5,
                },
                command=exec_command,
                ports={
                    evolution_broker_port: evolution_broker_port,
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
            )

            return container_id
        except docker.errors.APIError as e:
            if e.response.reason == "Not Found":
                raise DockerContainerNotFoundError(
                    f"The docker image {self.get_container().image} for the evolution broker could not be found!"
                )

            raise DockerError(e.explanation)
