from abc import ABC, abstractmethod
from typing import Any, Dict, List

from common.config.core import (
    get_core_defaults_dict,
)
from common.settings import Settings
from common.utils import deep_merge_dicts

from .config_sections.agents import agents_config_section
from .config_sections.atomdb import atomdb_config_section
from .config_sections.brokers import brokers_config_section
from .config_sections.service_params import params_config_section
from .config_sections.jupyter import jupyter_notebook_section

class ConfigProvider(ABC):

    def __init__(self, settings: Settings):
        super().__init__()

        self._settings = settings

    def _get_core_defaults(self) -> Dict[str, Any]:
        return get_core_defaults_dict()

    def _get_current_or_default_config(self) -> Dict[str, Any]:
        core_defaults = get_core_defaults_dict()
        new_schema_version = core_defaults.get("schema_version")

        user_settings=self._settings.get_content()

        core_defaults.update(user_settings)
        core_defaults["schema_version"] = new_schema_version
        # Always force new schema version, otherwise existing one will override.
        # Non-interactive will have to verify schema before call to avoid updating schema version without updating the rest of the file.
        # User on non-interactive will have to set-up the whole file again with the new schema before using the command.

        return core_defaults

    @abstractmethod
    def setup_settings(self) -> Dict[str, Any]:
        pass

    def raise_property_invalid(self, key: str) -> None:
        default_mappings = self._get_core_defaults()
        
        parts = key.split('.')
        current = default_mappings
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                raise AttributeError(f"'{key}' is not a valid configuration property.")

    def apply_values_to_settings(self, default_mappings: Dict):
        for default_key, default_value_or_func in default_mappings.items():
            if callable(default_value_or_func):
                if "nodes" in default_key:
                    self._settings.set(default_key)
                continue
            else:
                self._settings.set(default_key, default_value_or_func)

class InteractiveConfigProvider(ConfigProvider):
    def __init__(
        self,
        settings: Settings,
    ):
        super().__init__(settings)
        self._settings = settings

    def setup_settings(self) -> Dict[str, Any]:

        config_steps = [
            atomdb_config_section,
            agents_config_section,
            brokers_config_section,
            jupyter_notebook_section,
            params_config_section,
        ]

        config: Dict[str, Any] = {}

        for config_step in config_steps:
            config.update(config_step(settings=self._settings))

        final_config = {**self._get_current_or_default_config(), **config}

        return final_config


class NonInteractiveConfigProvider(ConfigProvider):
    def __init__(self, settings: Settings) -> None:
        super().__init__(settings)
        self._settings = settings

    def setup_settings(self) -> Dict[str, Any]:
        default_mappings = self._get_current_or_default_config()

        return default_mappings
