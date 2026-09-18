import os
import shutil
import json
from pathlib import Path
from typing import Optional

from injector import inject

from common import (
    Command,
    CommandArgument,
    CommandGroup,
    KeyValueType,
    RemoteContextManager,
    ServiceResponse,
    Settings,
    StdoutSeverity,
    StdoutStatus,
)
from common.utils import require_vault_endpoint
from common.config.defaults import get_default_config_dict
from settings.config import (
    DAS_PATH,
    DEFAULT_CONFIGFILE_PATH,
    PACKAGED_DEFAULT_CONFIGFILE_PATH,
    SYSTEM_DEFAULT_CONFIGFILE_PATH,
)

from .config_docs import (
    HELP_CONFIG,
    HELP_CONFIG_LIST,
    HELP_CONFIG_SET,
    SHORT_HELP_CONFIG,
    SHORT_HELP_CONFIG_LIST,
    SHORT_HELP_CONFIG_SET,
)
from .config_provider import NonInteractiveConfigProvider

CLI_SERVICE_NAME = "config"


class ConfigSet(Command):
    name = "set"

    short_help = SHORT_HELP_CONFIG_SET

    help = HELP_CONFIG_SET

    params = [
        CommandArgument(
            ["config_key_value"],
            required=False,
            type=KeyValueType(),
            # help="If provided, sets only the specified configuration key non-interactively.",
        ),
    ]

    @inject
    def __init__(
        self,
        settings: Settings,
        remote_context_manager: RemoteContextManager,
        non_interactive_config_provider: NonInteractiveConfigProvider,
    ) -> None:
        super().__init__()

        self._settings = settings
        self._remote_context_manager = remote_context_manager
        self._non_interactive_config_provider = non_interactive_config_provider

    def _finish_set(self, message: str) -> None:
        self.stdout(
            dict(
                ServiceResponse(
                    service=CLI_SERVICE_NAME,
                    action="set",
                    status=StdoutStatus.SUCCESS,
                    message=message,
                    path=self._settings.get_path(),
                    content=self._settings.get_content(),
                )
            ),
            severity=StdoutSeverity.SUCCESS,
        )

    def _save(self, save_path: str) -> None:
        self._remote_context_manager.commit()
        self._settings.set_path(save_path)
        self._settings.save()
        self._settings.save_path()

        config_path = self._settings.get_path()
        self._finish_set(f"Configuration file saved to {config_path}.")

    def _is_default_config_path(self, path: str) -> bool:
        active_path = Path(path).expanduser().resolve(strict=False)
        default_paths = {
            SYSTEM_DEFAULT_CONFIGFILE_PATH.resolve(strict=False),
            PACKAGED_DEFAULT_CONFIGFILE_PATH.resolve(strict=False),
        }
        return active_path in default_paths

    def _get_default_source_path(self) -> Path:
        source_path = Path(DEFAULT_CONFIGFILE_PATH).expanduser().resolve(strict=False)
        if not source_path.exists():
            raise FileNotFoundError(
                f"Default config not found: {source_path}. "
                "Reinstall package or verify system installation."
            )
        return source_path

    def _activate_default_config(self) -> None:
        source_path = self._get_default_source_path()
        self._remote_context_manager.commit()
        self._settings.set_path(str(source_path))
        self._settings.save_path()

        config_path = self._settings.get_path()
        self._finish_set(f"Configuration file set to -> {config_path}.")

    def _create_custom_config(self) -> None:
        config_name = Command.prompt(
            "Enter the custom config file name (it will be saved in ~/.das)",
            type=str,
        ).strip()

        if not config_name:
            raise ValueError("Config file name cannot be empty.")

        if "/" in config_name or "\\" in config_name:
            raise ValueError("Use only a file name, not a path.")

        if not config_name.endswith(".json"):
            config_name = f"{config_name}.json"

        save_path = str((DAS_PATH / config_name).resolve(strict=False))

        if os.path.exists(save_path):
            raise ValueError(
                f"Destination already exists: {save_path}. Please choose a new file path."
            )

        source_path = self._get_default_source_path()

        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        shutil.copyfile(str(source_path), save_path)

        with open(save_path, "w", encoding="utf-8") as config_file:
            json.dump(get_default_config_dict(), config_file, indent=4)

        self._remote_context_manager.commit()
        self._settings.set_path(save_path)
        self._settings.rewind()
        self._settings.save_path()

        config_path = self._settings.get_path()
        self._finish_set(f"Configuration file set to -> {config_path}.")

    def interactive_mode(self) -> None:
        mode = Command.select(
            text="Choose config setup mode",
            options={
                "Use default config": "default",
                "Create new custom config": "custom",
            },
            default="default",
        )

        if mode == "default":
            return self._activate_default_config()

        return self._create_custom_config()

    def non_interactive_mode(self, config_key_value: tuple) -> None:
        key, value = config_key_value

        active_config_path = self._settings.get_path()
        if self._is_default_config_path(active_config_path):
            raise ValueError(
                f"Cannot modify default config file: {active_config_path}\n"
                "Use: das-cli config set\n"
                "Then choose: Create new custom config"
            )

        self._non_interactive_config_provider.raise_property_invalid(key)

        if key == "vault.endpoint":
            require_vault_endpoint(value)

        config_mappings = self._non_interactive_config_provider.setup_settings()
        self._non_interactive_config_provider.apply_values_to_settings(config_mappings)
        self._settings.set(key, value)

        self._save(active_config_path)

    def run(
        self,
        config_key_value: Optional[tuple] = None,
    ):

        if config_key_value is not None:
            return self.non_interactive_mode(config_key_value)

        else:
            return self.interactive_mode()


class ConfigList(Command):
    name = "list"

    aliases = ["ls"]

    short_help = SHORT_HELP_CONFIG_LIST

    help = HELP_CONFIG_LIST

    params = [
        CommandArgument(
            ["key"],
            required=False,
            type=str,
        ),
    ]

    @inject
    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self._settings = settings

    def _show_config_key(self, key: str) -> None:
        value = self._settings.get(key, None)
        if value is None:
            self.stdout(
                dict(
                    ServiceResponse(
                        service=CLI_SERVICE_NAME,
                        action="list",
                        status=StdoutStatus.ERROR,
                        message=f"The key '{key}' does not exist in the configuration file.",
                        key=key,
                    )
                ),
                severity=StdoutSeverity.ERROR,
            )
            return

        self.log(str(value), severity=StdoutSeverity.INFO)
        self.stdout(
            dict(
                ServiceResponse(
                    service=CLI_SERVICE_NAME,
                    action="list",
                    status=StdoutStatus.SUCCESS,
                    message=f"Configuration key '{key}' listed successfully.",
                    path=self._settings.get_path(),
                    key=key,
                    value=value,
                )
            ),
            severity=StdoutSeverity.SUCCESS,
        )

    def _show_config(self) -> None:
        content = self._settings.get_content()
        config_path = self._settings.get_path()

        self.log(self._settings.pretty(), severity=StdoutSeverity.INFO)
        self.stdout(
            dict(
                ServiceResponse(
                    service=CLI_SERVICE_NAME,
                    action="list",
                    status=StdoutStatus.SUCCESS,
                    message="Configuration listed successfully.",
                    path=config_path,
                    content=content,
                )
            ),
            severity=StdoutSeverity.SUCCESS,
        )

    def run(self, key: Optional[str] = None):
        self._settings.validate_configuration_file()

        if not key:
            self._show_config()
        else:
            self._show_config_key(key)


class ConfigCli(CommandGroup):
    name = "config"

    aliases = ["cfg", "conf"]

    help = HELP_CONFIG

    short_help = SHORT_HELP_CONFIG

    @inject
    def __init__(
        self,
        configSet: ConfigSet,
        configList: ConfigList,
    ) -> None:
        super().__init__()

        self.add_commands(
            [
                configSet,
                configList,
            ]
        )
