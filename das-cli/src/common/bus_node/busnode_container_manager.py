from typing import Dict

import docker

from common.docker import ContainerManager
from common.docker.exceptions import DockerContainerDuplicateError
from .busnode_command_registry import BusNodeCommandRegistry
from common import Container, ContainerImageMetadata, ContainerMetadata
from settings.config import DAS_IMAGE_NAME, DAS_IMAGE_VERSION

class BusNodeContainerManager(ContainerManager):

    def __init__(
        self,
        container: Container,
        default_container_name: str,
        options: Dict = {},
    ) -> None:
        
        self._options = options

        self._cmd_registry = BusNodeCommandRegistry()

        container = Container(
            default_container_name,
            metadata=ContainerMetadata(
                port=self._options.get("service_port"),
                image=ContainerImageMetadata({
                        "name":DAS_IMAGE_NAME,
                        "version":DAS_IMAGE_VERSION
                    }
                )
            )
        )

        super().__init__(container)

    def start_container(self, ports_range: str, **kwargs) -> None:

        self.raise_running_container()
        self.raise_on_port_in_use([self._options.get("service_port")])

        try:

            service = self._options.get("service")
            endpoint = self._options.get("service_endpoint")

            bus_node_command = self._cmd_registry.build(service, endpoint, ports_range, **kwargs)

            container = self._start_container(
                restart_policy={
                    "Name": "on-failure",
                    "MaximumRetryCount": 5,
                },
                command=bus_node_command,
                environment={
                    "DAS_MONGODB_HOSTNAME": self._options.get("mongodb_hostname"),
                    "DAS_MONGODB_PORT": self._options.get("mongodb_port"),
                    "DAS_MONGODB_USERNAME": self._options.get("mongodb_username"),
                    "DAS_MONGODB_PASSWORD": self._options.get("mongodb_password"),
                    "DAS_REDIS_HOSTNAME": self._options.get("redis_hostname"),
                    "DAS_REDIS_PORT": self._options.get("redis_port"),
                    "DAS_MORK_HOSTNAME": self._options.get("morkdb_hostname"),
                    "DAS_MORK_PORT": self._options.get("morkdb_port"),
                },
            )
            return container

        except docker.errors.APIError as e:
            raise DockerContainerDuplicateError(e.explanation)
        
        except ValueError:
            raise ValueError("The service provided couldn't be found")
