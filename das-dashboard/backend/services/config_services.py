import json
import os
from io import BytesIO

from fastapi.concurrency import run_in_threadpool

from shared.dtos.configuration_entries_dto import ConfigurationEntriesDto
from shared.exceptions.custom_exceptions import CustomValueError
from shared.internal.configuration_constants import ATOMDB_TEMPLATES, CONSTANTS
from shared.internal.constants import CONFIG_PATH, REMOTE_CONFIG_PATH
from shared.internal.web_configuration import WebConfiguration
from shared.mappers.das_config_mapper import ConfigMapper
from shared.mappers.nested_config_mapper import NestedConfigMapper
from shared.utils.adapter_context_mapping import save_context_mapping_content
from shared.utils.das_cli_config import set_das_cli_config
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

        await run_in_threadpool(self._persist_config, nested_config)
        await run_in_threadpool(self.web_config.load_config_dictionary)
        await run_in_threadpool(
            set_das_cli_config,
            CONFIG_PATH,
            web_config=self.web_config,
        )

        return {"message": "Configuration saved successfully."}

    def _build_export_config(
        self,
        configuration_entries: ConfigurationEntriesDto | None = None,
    ) -> dict:
        if configuration_entries is not None:
            flat_payload = configuration_entries.model_dump(by_alias=True, exclude_none=True)
            if flat_payload:
                flat = merge_flat_config(flat_payload, CONSTANTS)
                return ConfigMapper.build_config(flat)

        flat = merge_flat_config({}, CONSTANTS)
        return ConfigMapper.build_config(flat)

    async def export_config(
        self,
        configuration_entries: ConfigurationEntriesDto | None = None,
    ) -> dict:
        return self._build_export_config(configuration_entries)

    async def export_targets(
        self,
        configuration_entries: ConfigurationEntriesDto | None = None,
    ) -> dict:
        nested = self._build_export_config(configuration_entries)
        return {"targets": self.web_config.map_hosts(nested)}

    def _export_config_scp_sync(self, ip: str, nested: dict) -> str:
        ssh = None
        try:
            ssh = self.remote_scp.connect(ip)
            home = self.remote_scp.get_remote_home(ssh)
            remote_dir = f"{home}/.das"
            remote_path = f"{home}{REMOTE_CONFIG_PATH}"

            self.remote_scp.transfer_fileobj(
                ip,
                BytesIO(json.dumps(nested, indent=2).encode("utf-8")),
                remote_path,
                remote_dir=remote_dir,
                ssh=ssh,
            )
            return remote_path
        finally:
            if ssh is not None:
                ssh.close()

    async def export_config_scp(
        self,
        ip: str,
        configuration_entries: ConfigurationEntriesDto | None = None,
    ) -> dict:
        nested = self._build_export_config(configuration_entries)
        known_ips = {target["ip"] for target in self.web_config.map_hosts(nested)}

        if ip not in known_ips:
            raise CustomValueError(
                message=f"IP '{ip}' is not configured in the current architecture."
            )

        remote_path = await run_in_threadpool(self._export_config_scp_sync, ip, nested)
        await run_in_threadpool(
            set_das_cli_config,
            remote_path,
            web_config=self.web_config,
            host=ip,
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

        await run_in_threadpool(self._persist_config, nested_config)
        flat = merge_flat_config(NestedConfigMapper.to_flat(nested_config), CONSTANTS)
        await run_in_threadpool(self.web_config.load_config_dictionary)
        await run_in_threadpool(
            set_das_cli_config,
            CONFIG_PATH,
            web_config=self.web_config,
        )

        return flat

    def get_config_defaults(self, *, factory: bool = False) -> dict:
        if factory:
            return self._factory_defaults_response()

        flat = merge_flat_config({}, CONSTANTS)

        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as config_file:
                    nested = json.load(config_file)

                if isinstance(nested, list) and nested:
                    nested = nested[0]

                if isinstance(nested, dict):
                    saved_flat = NestedConfigMapper.to_flat(nested)
                    flat = merge_flat_config(saved_flat, CONSTANTS)
            except (OSError, json.JSONDecodeError, TypeError, ValueError, IndexError):
                pass

        return self._defaults_response(flat)

    def _factory_defaults_response(self) -> dict:
        flat = merge_flat_config({}, CONSTANTS)
        return self._defaults_response(flat)

    def _defaults_response(self, flat: dict) -> dict:
        atomdb_templates = dict(ATOMDB_TEMPLATES)
        atomdb_section = flat.get("atomdb")

        if isinstance(atomdb_section, dict) and atomdb_section.get("atomdb_type"):
            atomdb_templates[atomdb_section["atomdb_type"]] = atomdb_section

        return {
            "content": flat,
            "atomdb_templates": atomdb_templates,
        }

    async def save_context_mapping(self, content: str | None = None, path: str | None = None) -> dict:
        if path is not None:
            cleaned_path = (path or "").strip()
            if not cleaned_path:
                raise ValueError("Context mapping path is required.")

            return {
                "message": "Context mapping path noted. Apply AtomDB settings to include it in the config.",
                "saved_path": cleaned_path,
            }

        return save_context_mapping_content(content or "")

    def _persist_config(self, nested_config: dict) -> None:
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)

        with open(CONFIG_PATH, "w", encoding="utf-8") as output:
            output.write(json.dumps(nested_config, indent=2))
