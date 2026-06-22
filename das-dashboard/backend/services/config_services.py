import json
import os

from shared.dtos.configuration_entries_dto import ConfigurationEntriesDto
from shared.internal.configuration_constants import CONSTANTS
from shared.internal.constants import CONFIG_PATH, REMOTE_CONFIG_PATH
from shared.internal.web_configuration import WebConfiguration
from shared.mappers.das_config_mapper import ConfigMapper
from shared.mappers.nested_config_mapper import NestedConfigMapper
from shared.utils.adapter_context_mapping import (
    save_context_mapping_content,
    save_context_mapping_path,
    sync_context_mapping_from_nested,
)
from shared.utils.flat_config_utils import merge_flat_config
from shared.utils.remote_scp import RemoteScpService


class ConfigServices:

    def __init__(self, web_config: WebConfiguration):
        self.web_config = web_config
        self.remote_scp = RemoteScpService(web_config)

    async def save_config(self, configuration_entries: ConfigurationEntriesDto) -> dict:
        flat = merge_flat_config(
            configuration_entries.model_dump(by_alias=True, exclude_none=True),
            CONSTANTS,
        )
        nested_config = ConfigMapper.build_config(flat)

        self._persist_config(nested_config)
        self.web_config.load_config_dictionary()

        return {"message": "Configuration saved successfully."}

    def _require_saved_config(self) -> dict:
        nested = self._load_nested_config()
        if not nested:
            raise ValueError("Save the configuration before exporting.")
        return nested

    async def has_saved_config(self) -> bool:
        return self._load_nested_config() is not None

    async def export_config(self) -> dict:
        return self._require_saved_config()

    async def export_targets(self) -> dict:
        nested = self._require_saved_config()
        return {"targets": self.web_config.map_hosts(nested)}

    async def export_config_scp(self, ip: str) -> dict:
        nested = self._require_saved_config()
        known_ips = {target["ip"] for target in self.web_config.map_hosts(nested)}

        if ip not in known_ips:
            raise ValueError(f"IP '{ip}' is not configured in the current architecture.")

        ssh = self.remote_scp.connect(ip)
        try:
            home = self.remote_scp.get_remote_home(ssh)
            remote_dir = f"{home}/.das"
            remote_path = f"{home}{REMOTE_CONFIG_PATH}"
        finally:
            ssh.close()

        self.remote_scp.transfer_bytes(
            ip,
            json.dumps(nested, indent=2).encode("utf-8"),
            remote_path,
            remote_dir=remote_dir,
        )

        return {
            "message": f"Configuration exported to {ip}.",
            "remote_path": remote_path,
        }

    async def load_config(self, nested_config: dict) -> dict:
        if not isinstance(nested_config, dict):
            raise ValueError("Configuration must be a JSON object.")

        if "atomdb" not in nested_config or "agents" not in nested_config:
            raise ValueError("Configuration must include 'atomdb' and 'agents' sections.")

        sync_context_mapping_from_nested(nested_config)
        self._persist_config(nested_config)
        flat = merge_flat_config(NestedConfigMapper.to_flat(nested_config), CONSTANTS)
        self.web_config.load_config_dictionary()

        return flat

    async def save_context_mapping(self, content: str | None = None, path: str | None = None) -> dict:
        if path is not None:
            return save_context_mapping_path(path)

        return save_context_mapping_content(content or "")

    def _load_nested_config(self) -> dict | None:
        if not os.path.exists(CONFIG_PATH):
            return None

        with open(CONFIG_PATH, "r", encoding="utf-8") as config_file:
            config_dict = json.load(config_file)

        if isinstance(config_dict, list):
            config_dict = config_dict[0]

        if isinstance(config_dict, dict) and "atomdb" in config_dict and "agents" in config_dict:
            return config_dict

        return None

    def _persist_config(self, nested_config: dict) -> None:
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)

        with open(CONFIG_PATH, "w", encoding="utf-8") as output:
            output.write(json.dumps(nested_config, indent=2))
