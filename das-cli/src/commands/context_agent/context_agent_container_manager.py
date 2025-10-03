from typing import Dict

import docker

from common import Container, ContainerImageMetadata, ContainerManager
from common.docker.exceptions import DockerContainerNotFoundError, DockerError
from settings.config import CONTEXT_AGENT_IMAGE_NAME, CONTEXT_AGENT_IMAGE_VERSION


class ContextAgentContainerManager(ContainerManager):
    def __init__(
        self,
        context_agent_container_name: str,
        options: Dict = {},
    ) -> None:
        container = Container(
            context_agent_container_name,
            metadata={
                "port": options.get("context_agent_port"),
                "image": ContainerImageMetadata(
                    {
                        "name": CONTEXT_AGENT_IMAGE_NAME,
                        "version": CONTEXT_AGENT_IMAGE_VERSION,
                    }
                ),
            },
        )
        self._options = options

        super().__init__(container)

    def _gen_context_agent_command(
        self,
        peer_hostname: str,
        peer_port: str,
        port_range: str,
    ) -> str:
        context_agent_hostname = self._options.get(
            "context_agent_hostname",
            "localhost",
        )
        context_agent_port = int(self._options.get("context_agent_port", 0))
        context_agent_address = f"{context_agent_hostname}:{context_agent_port}"

        peer_address = f"{peer_hostname}:{peer_port}"

        attention_broker_hostname = self._options.get(
            "attention_broker_hostname",
            "localhost",
        )
        attention_broker_port = int(self._options.get("attention_broker_port", 0))
        attention_broker_address = (
            f"{attention_broker_hostname}:{attention_broker_port}"
        )

        return f"{context_agent_address} {port_range} {peer_address} {attention_broker_address}"

    def start_container(
        self,
        peer_hostname: str,
        peer_port: int,
        port_range: str,
    ):
        self.raise_running_container()
        self.raise_on_port_in_use([int(self._options.get("context_agent_port", 0))])

        try:
            self.stop()
        except (DockerContainerNotFoundError, DockerError):
            pass

        try:
            exec_command = self._gen_context_agent_command(
                peer_hostname,
                peer_port,
                port_range,
            )
            context_agent_port = self._options.get("context_agent_port", 0)

            container_id = self._start_container(
                restart_policy={
                    "Name": "on-failure",
                    "MaximumRetryCount": 5,
                },
                command=exec_command,
                ports={
                    context_agent_port: context_agent_port,
                },
                environment={
                    "DAS_MONGODB_HOSTNAME": self._options.get("mongodb_hostname"),
                    "DAS_MONGODB_PORT": self._options.get("mongodb_port"),
                    "DAS_MONGODB_USERNAME": self._options.get("mongodb_username"),
                    "DAS_MONGODB_PASSWORD": self._options.get("mongodb_password"),
                    "DAS_REDIS_HOSTNAME": self._options.get("redis_hostname"),
                    "DAS_REDIS_PORT": self._options.get("redis_port"),
                },
            )

            return container_id
        except docker.errors.APIError as e:
            if e.response.reason == "Not Found":
                raise DockerContainerNotFoundError(
                    f"The docker image {self.get_container().image} for the context agent could not be found!"
                )

            raise DockerError(e.explanation)
