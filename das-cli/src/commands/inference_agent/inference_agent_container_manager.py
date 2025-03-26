import tempfile
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


    def _create_temp_config_file(self,
        inference_agent_hostname: str,                         
        inference_agent_port: int,
        link_creation_agent_client_hostname: str,
        link_creation_agent_client_port: int,
        link_creation_agent_server_hostname: str,
        link_creation_agent_server_port: int,
        das_client_hostname: str,
        das_client_port: int,
        das_server_hostname: str,
        das_server_port: int,
        distributed_inference_control_node_hostname: str,
        distributed_inference_control_node_port: int,
        distributed_inference_control_node_server_hostname: str,
        distributed_inference_control_node_server_port: int
    ) -> str:
        config_data = f"""
inference_node_id = {inference_agent_hostname}:{inference_agent_port}
link_creation_agent_client_id = {link_creation_agent_client_hostname}:{link_creation_agent_client_port}
link_creation_agent_server_id = {link_creation_agent_server_hostname}:{link_creation_agent_server_port}
das_client_id = {das_client_hostname}:{das_client_port}
das_server_id = {das_server_hostname}:{das_server_port}
distributed_inference_control_node_id = {distributed_inference_control_node_hostname}:{distributed_inference_control_node_port}
distributed_inference_control_node_server_id = {distributed_inference_control_node_server_hostname}:{distributed_inference_control_node_server_port}
"""
        with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".conf") as temp_file:
            temp_file.write(config_data)
            return temp_file.name

    def get_ports_in_use(self):
        return [
            self._options.get('inference_agent_port'),
            self._options.get('link_creation_agent_client_port'),
            self._options.get('das_client_port'),
            self._options.get('distributed_inference_control_node_port'),
        ]

    def start_container(self):
        self.raise_running_container()
        self.raise_on_port_in_use(self.get_ports_in_use())

        try:
            self.stop()
        except (DockerContainerNotFoundError, DockerError):
            pass

        config_file_path = self._create_temp_config_file(
            inference_agent_hostname=self._options.get('inference_agent_hostname'),
            inference_agent_port=self._options.get('inference_agent_port'),
            link_creation_agent_client_hostname=self._options.get('link_creation_agent_client_hostname'),
            link_creation_agent_client_port=self._options.get('link_creation_agent_client_port'),
            link_creation_agent_server_hostname=self._options.get('link_creation_agent_server_hostname'),
            link_creation_agent_server_port=self._options.get('link_creation_agent_server_port'),
            das_client_hostname=self._options.get('das_client_hostname'),
            das_client_port=self._options.get('das_client_port'),
            das_server_hostname=self._options.get('das_server_hostname'),
            das_server_port=self._options.get('das_server_port'),
            distributed_inference_control_node_hostname=self._options.get('distributed_inference_control_node_hostname'),
            distributed_inference_control_node_port=self._options.get('distributed_inference_control_node_port'),
            distributed_inference_control_node_server_hostname=self._options.get('distributed_inference_control_node_server_hostname'),
            distributed_inference_control_node_server_port=self._options.get('distributed_inference_control_node_server_port'),
        )

        try:
            volumes = {
                config_file_path: {
                    "bind": config_file_path,
                    "mode": "ro",
                }
            }

            exec_command = f"--config_file {config_file_path}"

            container_id = self._start_container(
                network_mode="host",
                restart_policy={
                    "Name": "on-failure",
                    "MaximumRetryCount": 5,
                },
                command=exec_command,
                volumes=volumes,
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
