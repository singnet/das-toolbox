from typing import Dict

import docker

from common import Container, ContainerImageMetadata, ContainerMetadata
from common.docker import ContainerManager
from common.docker.exceptions import DockerContainerDuplicateError
from settings.config import CURRENT_CONFIGFILE_PATH, DAS_IMAGE_NAME, DAS_IMAGE_VERSION

from ..bus_node.busnode_command_registry import BusNodeCommandRegistry


class BusNodeContainerManager(ContainerManager):
    def __init__(
        self,
        default_container_name: str,
        options: Dict = {},
    ) -> None:
        self._options = options

        self._cmd_registry = BusNodeCommandRegistry()

        container = Container(
            default_container_name,
            metadata=ContainerMetadata(
                port=self._options.get("service_port"),
                image=ContainerImageMetadata(
                    {"name": DAS_IMAGE_NAME, "version": DAS_IMAGE_VERSION}
                ),
            ),
        )

        super().__init__(container)

    def start_container(self, ports_range: str) -> None:
        self.raise_running_container()
        self.raise_on_port_in_use([self._options.get("service_port")])

        user_config_volume = CURRENT_CONFIGFILE_PATH

        try:
            service = self._options.get("service")
            endpoint = self._options.get("service_endpoint")
            bus_node_command = self._cmd_registry.build(
                service,
                endpoint,
                ports_range,
                self._options,
            )

            container = self._start_container(
                restart_policy={
                    "Name": "on-failure",
                    "MaximumRetryCount": 5,
                },
                volumes={
                    user_config_volume: {
                        "bind": CURRENT_CONFIGFILE_PATH,
                        "mode": "ro",
                    },
                    **self._build_adapterdb_mapping_volumes(),
                    **self._build_metta_output_dir(),
                },
                command=bus_node_command,
            )
            return container

        except docker.errors.APIError as e:
            raise DockerContainerDuplicateError(e.explanation)

        except ValueError:
            raise ValueError("The service provided couldn't be found")

    def _build_adapterdb_mapping_volumes(self):
        adapterdb_context_maps = self._options.get("adapterdb_context_maps") or []
        return {path: {"bind": path, "mode": "ro"} for path in adapterdb_context_maps}

    def _build_metta_output_dir(self):
        metta_output_dir = self._options.get("metta_mapping_output_dir")
        if not metta_output_dir:
            return {}

        return {
            metta_output_dir: {
                "bind": metta_output_dir,
                "mode": "ro",
            }
        }
