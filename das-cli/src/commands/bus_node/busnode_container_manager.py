from common.docker import Container, ContainerManager
from common.docker.exceptions import *
from settings.config import DAS_IMAGE_NAME, DAS_IMAGE_VERSION
from typing import Dict
from common import ContainerImageMetadata, ContainerMetadata
import docker

class BusNodeContainerManager(ContainerManager):

    def __init__(
        self,
        default_container_name: str,
        options: Dict = {},
    ) -> None:
        container = Container(
            default_container_name,
            metadata={
                "port": options.get("busnode_port"),
                "image":ContainerImageMetadata(
                    {
                        "name": DAS_IMAGE_NAME,
                        "version": DAS_IMAGE_VERSION,
                    }
                ),
            },
        )
        self._options = options

        super().__init__(container)
    

    def _gen_bus_node_command(
        self,
        service: str,
        endpoint: str,
        ports_range: str,
    ) -> str:

        command = f"busnode --service={service} --endpoint={endpoint} --ports-range={ports_range}"

        return command
    
    def _set_bus_node_container_name(self, service: str=None, endpoint:str=None, node_name:str = None) -> None:

        if node_name:
            self._container._name = node_name

        else:
            host, port = endpoint.split(":")

            container_name = f"das-cli-busnode-{port}-{service}" if node_name is None else node_name

            self._container._name = container_name

    def stop(self, node_name=None) -> None:
        self._set_bus_node_container_name("", "", node_name)

        super().stop()

    def start_container(
        self,
        service: str,
        endpoint: str,
        ports_range: str,
    ) -> None:

        try:

            bus_node_command = self._gen_bus_node_command(
                service,
                endpoint,
                ports_range,
            )

            self._set_bus_node_container_name(service,endpoint)

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