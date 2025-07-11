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

    def _get_port_range(self, port_range: str) -> list[int]:
        if not port_range or ":" not in port_range:
            raise ValueError("Invalid port range format. Expected 'start:end'.")

        start_port, end_port = map(int, port_range.split(":"))
        if start_port >= end_port:
            raise ValueError("Invalid port range. Start port must be less than end port.")

        return list(range(start_port, end_port + 1))

    def _gen_link_creation_command(
        self,
        peer_hostname: str,
        peer_port: int,
        port_range: str,
        metta_file_path: str,
        buffer_file: str,
    ) -> str:
        link_creation_agent_hostname = str(self._options.get("link_creation_agent_hostname", ""))
        link_creation_agent_port = int(self._options.get("link_creation_agent_port", 0))

        request_interval = int(self._options.get("link_creation_agent_request_interval", 1))
        thread_count = int(self._options.get("link_creation_agent_thread_count", 1))
        default_timeout = int(self._options.get("link_creation_agent_default_timeout", 10))
        save_links_to_metta_file = bool(
            self._options.get("link_creation_agent_save_links_to_metta_file", True)
        )
        save_links_to_db = bool(self._options.get("link_creation_agent_save_links_to_db", True))

        server_address = f"{link_creation_agent_hostname}:{link_creation_agent_port}"
        peer_address = f"{peer_hostname}:{peer_port}"

        return f"{server_address} {peer_address} {port_range} {request_interval} {thread_count} {default_timeout} {buffer_file} {metta_file_path} {save_links_to_metta_file} {save_links_to_db}"

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
        metta_file_path: str,
    ) -> str:
        self.raise_running_container()
        self.raise_on_port_in_use(
            [
                self._options.get("link_creation_agent_port"),
                *self._get_port_range(port_range),
            ]
        )

        try:
            self.stop()
        except (DockerContainerNotFoundError, DockerError):
            pass

        buffer_file = str(self._options.get("link_creation_agent_buffer_file"))

        self._ensure_file_exists(buffer_file)

        buffer_file_container = "/tmp/requests_buffer.bin"
        metta_file_path_container = "/tmp/metta_files"

        volumes = {
            metta_file_path: {
                "bind": metta_file_path_container,
                "mode": "ro",
            },
            buffer_file: {
                "bind": buffer_file_container,
                "mode": "rw",
            },
        }

        exec_command = self._gen_link_creation_command(
            peer_hostname,
            peer_port,
            port_range,
            metta_file_path,
            buffer_file_container,
        )

        try:
            container_id = self._start_container(
                network_mode="host",
                restart_policy={
                    "Name": "on-failure",
                    "MaximumRetryCount": 5,
                },
                volumes=volumes,
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
            )

            return container_id
        except docker.errors.APIError as e:
            if e.response.reason == "Not Found":
                raise DockerContainerNotFoundError(
                    f"The docker image {self.get_container().image} for the link creation agent could not be found!"
                )

            raise DockerError(e.explanation)
