from common.docker import ContainerManager, Container
from common.docker.container_manager import ContainerImageMetadata, ContainerMetadata
from settings.config import DAS_IMAGE_NAME, DAS_IMAGE_VERSION, CURRENT_CONFIGFILE_PATH

from typing import Dict, Union

class DatabaseAdapterContainerManager(ContainerManager):

    def __init__(self, container_name, options : Dict, exec_context: Union[str, None] = None):
        self._options = options

        container = Container(
            container_name,
            metadata=ContainerMetadata(
                port=self._options.get("service_port", None),
                image=ContainerImageMetadata(
                    {"name": DAS_IMAGE_NAME, "version": DAS_IMAGE_VERSION}
                ),
            ),
        )

        super().__init__(container)

    def start_container(self):
        command = self._build_adapter_command()
        user_config = CURRENT_CONFIGFILE_PATH

        self._start_container(
            volumes={
                user_config: {
                    "bind": CURRENT_CONFIGFILE_PATH,
                    "mode": "ro",
                },
                **self._build_adapterdb_mapping_volumes(),
                **self._build_metta_output_dir(),
            },
            command=command
        )
    
    def _build_adapter_command(self):
        return f"database_adapter {CURRENT_CONFIGFILE_PATH}"
    
    def _build_adapterdb_mapping_volumes(self):
        adapterdb_context_maps = self._options.get("context_mapping_paths") or []

        if not adapterdb_context_maps:
            return {}

        return {path: {"bind": path, "mode": "ro"} for path in adapterdb_context_maps}

    def _build_metta_output_dir(self):
        metta_output_dir = self._options.get("metta_output_dir")

        if not metta_output_dir:
            return {}

        return {
            metta_output_dir: {
                "bind": metta_output_dir,
                "mode": "ro",
            }
        }