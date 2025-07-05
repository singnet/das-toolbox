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

    def _gen_inference_command(
        self,
        peer_hostname: str,
        peer_port: int,
        port_range: str,
    ) -> str:
        inference_agent_hostname = str(
            self._options.get("inference_agent_hostname", "")
        )
        inference_agent_port = int(self._options.get("inference_agent_port", 0))

        server_address = f"{inference_agent_hostname}:{inference_agent_port}"
        peer_address = f"{peer_hostname}:{peer_port}"

        return f"{server_address} {peer_address} {port_range}"

    def _get_port_range(self, port_range: str) -> list[int]:
        if not port_range or ":" not in port_range:
            raise ValueError("Invalid port range format. Expected 'start:end'.")

        start_port, end_port = map(int, port_range.split(":"))
        if start_port >= end_port:
            raise ValueError(
                "Invalid port range. Start port must be less than end port."
            )

        return list(range(start_port, end_port + 1))

    def start_container(
        self,
        peer_hostname: str,
        peer_port: int,
        port_range: str,
    ):
        self.raise_running_container()
        self.raise_on_port_in_use(
            [
                self._options.get("inference_agent_port"),
                *self._get_port_range(port_range),
            ]
        )

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
