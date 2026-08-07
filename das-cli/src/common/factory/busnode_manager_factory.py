import os

from common import Settings
from common.config.store import JsonConfigStore
from common.utils import extract_service_hostname, extract_service_port
from settings.config import SECRETS_PATH

from ..container_manager.busnode_container_manager import BusNodeContainerManager


class BusNodeContainerManagerFactory:
    def __init__(self):
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

    def format_service_name(self, service_name: str) -> str:

        if service_name.__contains__("-"):
            formatted_name = service_name.replace("-", " ").title()

            return formatted_name

        else:
            formatted_name = service_name.capitalize()
            return formatted_name

    def build(self, use_settings_from: str, service_name: str) -> BusNodeContainerManager:

        service_port = extract_service_port(self._settings.get(f"{use_settings_from}.endpoint"))
        service_endpoint = f"0.0.0.0:{service_port}"

        attention_broker_hostname = extract_service_hostname(
            self._settings.get("agents.attention.endpoint")
        )

        attention_broker_port = extract_service_port(
            self._settings.get("agents.attention.endpoint")
        )

        adapterdb_context_mappings = self._settings.get(
            "atomdb.adapterdb.context_mapping_paths", None
        )

        metta_mapping_output_dir = self._settings.get(
            "atomdb.adapterdb.export_metta_on_mapping.output_dir"
        )

        default_container_name = f"das-{service_name}-{service_port}"

        default_bus_endpoint = extract_service_hostname(self._settings.get("agents.query.endpoint"))
        default_bus_port = extract_service_port(self._settings.get("agents.query.endpoint"))

        return BusNodeContainerManager(
            default_container_name,
            options={
                "service": service_name,
                "service_name": self.format_service_name(service_name),
                "service_command_label": service_name,
                "service_port": service_port,
                "service_endpoint": service_endpoint,
                "default_bus_endpoint": default_bus_endpoint,
                "default_bus_port": default_bus_port,
                "attention_broker_hostname": attention_broker_hostname,
                "attention_broker_port": attention_broker_port,
                "adapterdb_context_maps": adapterdb_context_mappings,
                "metta_mapping_output_dir": metta_mapping_output_dir,
            },
        )
