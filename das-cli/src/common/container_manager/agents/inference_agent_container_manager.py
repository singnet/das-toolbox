from typing import Dict

import docker

from common import Container, ContainerImageMetadata, ContainerManager
from common.docker.exceptions import DockerContainerNotFoundError, DockerError
from common.factory.atomdb.atomdb_backend import AtomdbBackendEnum
from settings.config import DAS_IMAGE_NAME, DAS_IMAGE_VERSION


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
                        "name": DAS_IMAGE_NAME,
                        "version": DAS_IMAGE_VERSION,
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
        inference_agent_hostname = str(self._options.get("inference_agent_hostname", ""))
        inference_agent_port = int(self._options.get("inference_agent_port", 0))

        server_address = f"{inference_agent_hostname}:{inference_agent_port}"
        peer_address = f"{peer_hostname}:{peer_port}"

        attention_broker_hostname = str(self._options.get("attention_broker_hostname", ""))
        attention_broker_port = int(self._options.get("attention_broker_port", 0))

        attention_broker_address = f"{attention_broker_hostname}:{attention_broker_port}"

        atomdb_backend = self._options.get("atomdb_backend")

        use_mork = atomdb_backend == AtomdbBackendEnum.MORK_MONGODB.value

        use_mork_flag = "--use-mork" if use_mork else "--use-mongodb"

        return f"inference_agent_server {server_address} {peer_address} {port_range} {attention_broker_address} {use_mork_flag}".strip()

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
                restart_policy={
                    "Name": "on-failure",
                    "MaximumRetryCount": 5,
                },
                environment={
                    "DAS_MONGODB_HOSTNAME": self._options.get("mongodb_hostname"),
                    "DAS_MONGODB_PORT": self._options.get("mongodb_port"),
                    "DAS_MONGODB_USERNAME": self._options.get("mongodb_username"),
                    "DAS_MONGODB_PASSWORD": self._options.get("mongodb_password"),
                    "DAS_REDIS_HOSTNAME": self._options.get("redis_hostname"),
                    "DAS_REDIS_PORT": self._options.get("redis_port"),
                    "DAS_ATTENTION_BROKER_ADDRESS": self._options.get("attention_broker_hostname"),
                    "DAS_ATTENTION_BROKER_PORT": self._options.get("attention_broker_port"),
                    "DAS_MORK_HOSTNAME": self._options.get("morkdb_hostname"),
                    "DAS_MORK_PORT": self._options.get("morkdb_port"),
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
