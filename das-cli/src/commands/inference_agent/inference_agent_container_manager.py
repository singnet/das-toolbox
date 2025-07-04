from typing import Dict

import docker

from common import Container, ContainerImageMetadata, ContainerManager
from common.docker.exceptions import DockerContainerNotFoundError, DockerError
from settings.config import INFERENCE_AGENT_IMAGE_NAME, INFERENCE_AGENT_IMAGE_VERSION


class InferenceAgentContainerManager(ContainerManager):
    def __init__(
        self,
        inference_agent_container_name: str,
        options: Dict = {},
    ) -> None:
        container = Container(
            inference_agent_container_name,
            metadata={
                "port": options.get("inference_agent_port"),
                "image": ContainerImageMetadata(
                    {
                        "name": INFERENCE_AGENT_IMAGE_NAME,
                        "version": INFERENCE_AGENT_IMAGE_VERSION,
                    }
                ),
            },
        )
        self._options = options

        super().__init__(container)

    def get_ports_in_use(self):
        return [
            self._options.get("inference_agent_port"),
            self._options.get("link_creation_agent_client_port"),
            self._options.get("das_client_port"),
            self._options.get("distributed_inference_control_node_port"),
        ]

    def _gen_inference_command(self, peer_hostname, peer_port, port_range):
        inference_agent_hostname = str(
            self._options.get("inference_agent_hostname", "")
        )
        inference_agent_port = int(self._options.get("inference_agent_port", 0))

        server_address = f"{inference_agent_hostname}:{inference_agent_port}"
        peer_address = f"{peer_hostname}:{peer_port}"

        return f"{server_address} {peer_address} {port_range}"

    def start_container(
        self,
        peer_hostname: str,
        peer_port: int,
        port_range: str,
    ):
        self.raise_running_container()
        self.raise_on_port_in_use(self.get_ports_in_use())

        try:
            self.stop()
        except (DockerContainerNotFoundError, DockerError):
            pass

        try:
            exec_command = self._gen_inference_command(
                peer_hostname,
                peer_port,
                port_range,
            )

            container_id = self._start_container(
                network_mode="host",
                restart_policy={
                    "Name": "on-failure",
                    "MaximumRetryCount": 5,
                },
                command=exec_command,
                stdin_open=True,
                tty=True,
            )

            return container_id
        except docker.errors.APIError as e:
            if e.response.reason == "Not Found":
                raise DockerContainerNotFoundError(
                    f"The docker image {self.get_container().image} for the inference agent could not be found!"
                )

            raise DockerError(e.explanation)
