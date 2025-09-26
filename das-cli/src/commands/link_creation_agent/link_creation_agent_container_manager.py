import os
from typing import Dict

import docker

from common import Container, ContainerImageMetadata, ContainerManager
from common.docker.exceptions import DockerContainerNotFoundError, DockerError
from settings.config import LINK_CREATION_AGENT_IMAGE_NAME, LINK_CREATION_AGENT_IMAGE_VERSION


class LinkCreationAgentContainerManager(ContainerManager):
    def __init__(
        self,
        link_creation_agent_container_name: str,
        options: Dict = {},
    ) -> None:
        container = Container(
            link_creation_agent_container_name,
            metadata={
                "port": options.get("link_creation_agent_port"),
                "image": ContainerImageMetadata(
                    {
                        "name": LINK_CREATION_AGENT_IMAGE_NAME,
                        "version": LINK_CREATION_AGENT_IMAGE_VERSION,
                    }
                ),
            },
        )
        self._options = options

        super().__init__(container)

    def _gen_link_creation_command(
        self,
        peer_hostname: str,
        peer_port: int,
        port_range: str,
    ) -> str:
        link_creation_agent_hostname = str(self._options.get("link_creation_agent_hostname", ""))
        link_creation_agent_port = int(self._options.get("link_creation_agent_port", 0))

        server_address = f"{link_creation_agent_hostname}:{link_creation_agent_port}"
        peer_address = f"{peer_hostname}:{peer_port}"

        return f"{server_address} {peer_address} {port_range}"

    def _ensure_file_exists(self, path: str) -> None:
        if os.path.exists(path):
            if os.path.isfile(path):
                return
            else:
                raise RuntimeError(f"The path '{path}' exists but is not a file.")

        try:
            with open(path, "wb") as _:
                pass
        except Exception as e:
            raise RuntimeError(f"Failed to create file '{path}': {e}")

    def start_container(
        self,
        peer_hostname: str,
        peer_port: int,
        port_range: str,
    ) -> str:
        self.raise_running_container()
        self.raise_on_port_in_use(
            [
                self._options.get("link_creation_agent_port"),
            ]
        )

        try:
            self.stop()
        except (DockerContainerNotFoundError, DockerError):
            pass

        buffer_file = str(self._options.get("link_creation_agent_buffer_file"))

        self._ensure_file_exists(buffer_file)

        exec_command = self._gen_link_creation_command(
            peer_hostname,
            peer_port,
            port_range,
        )
        link_creation_agent_port = int(self._options.get("link_creation_agent_port", 0))

        try:
            container_id = self._start_container(
                restart_policy={
                    "Name": "on-failure",
                    "MaximumRetryCount": 5,
                },
                command=exec_command,
                stdin_open=True,
                tty=True,
                environment={
                    "DAS_REDIS_HOSTNAME": self._options.get("redis_hostname"),
                    "DAS_REDIS_PORT": self._options.get("redis_port"),
                    "DAS_USE_REDIS_CLUSTER": self._options.get("redis_cluster"),
                    "DAS_MONGODB_HOSTNAME": self._options.get("mongodb_hostname"),
                    "DAS_MONGODB_PORT": self._options.get("mongodb_port"),
                    "DAS_MONGODB_USERNAME": self._options.get("mongodb_username"),
                    "DAS_MONGODB_PASSWORD": self._options.get("mongodb_password"),
                    "DAS_ATTENTION_BROKER_ADDRESS": self._options.get("attention_broker_hostname"),
                    "DAS_ATTENTION_BROKER_PORT": self._options.get("attention_broker_port"),
                },
                ports={
                    link_creation_agent_port: link_creation_agent_port,
                },
            )

            return container_id
        except docker.errors.APIError as e:
            if e.response.reason == "Not Found":
                raise DockerContainerNotFoundError(
                    f"The docker image {self.get_container().image} for the link creation agent could not be found!"
                )

            raise DockerError(e.explanation)
