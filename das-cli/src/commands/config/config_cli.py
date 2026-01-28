from typing import Optional

from injector import inject

from common import (
    Command,
    CommandArgument,
    CommandGroup,
    CommandOption,
    KeyValueType,
    RemoteContextManager,
    Settings,
    StdoutSeverity,
    StdoutType,
)
from common.config.loader import CompositeLoader, EnvFileLoader, EnvVarLoader
from common.prompt_types import AbsolutePath

from .config_docs import (
    HELP_CONFIG,
    HELP_CONFIG_LIST,
    HELP_CONFIG_SET,
    SHORT_HELP_CONFIG,
    SHORT_HELP_CONFIG_LIST,
    SHORT_HELP_CONFIG_SET,
)
from .config_provider import InteractiveConfigProvider, NonInteractiveConfigProvider


class ConfigSet(Command):
    name = "set"

    short_help = SHORT_HELP_CONFIG_SET

    help = HELP_CONFIG_SET

    params = [
        CommandOption(
            ["--from-env"],
            help="Path to an environment file to load initial configuration values from to be suggested as the default value in the interactive prompts.",
            required=False,
            type=AbsolutePath(
                file_okay=True,
                dir_okay=False,
                exists=True,
                writable=True,
                readable=True,
            ),
        ),
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
        interactive_config_provider: InteractiveConfigProvider,
    ) -> None:
        super().__init__()

        self._settings = settings
        self._settings.enable_overwrite_mode()
        self._remote_context_manager = remote_context_manager
        self._non_interactive_config_provider = non_interactive_config_provider
        self._interactive_config_provider = interactive_config_provider

    def _save(self) -> None:
        self._remote_context_manager.commit()
        self._settings.save()
        self.stdout(
            f"Configuration file saved -> {self._settings.get_dir_path()}",
            severity=StdoutSeverity.SUCCESS,
        )

    def interactive_mode(self, from_env: Optional[str]) -> None:
        self._settings.replace_loader(
            loader=CompositeLoader(
                [
                    EnvFileLoader(from_env),
                    EnvVarLoader(),
                ]
            )
        )

        config_mappings = self._interactive_config_provider.get_all_configs()
        self._interactive_config_provider.apply_default_values(config_mappings)
        self._interactive_config_provider.recalculate_config_dynamic_values(config_mappings)
        self._save()

    def non_interactive_mode(self, config_key_value: tuple) -> None:
        key, value = config_key_value

        default_mappings = self._non_interactive_config_provider.get_all_configs()
        self._non_interactive_config_provider.raise_property_invalid(key)
        self._non_interactive_config_provider.apply_default_values(default_mappings)
        self._settings.set(key, value)
        self._non_interactive_config_provider.recalculate_config_dynamic_values(default_mappings)
        self._save()

    def run(
        self,
        from_env: Optional[str] = None,
        config_key_value: Optional[tuple] = None,
    ):
        if config_key_value:
            return self.non_interactive_mode(config_key_value)

        return self.interactive_mode(from_env=from_env)


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
                f"The key '{key}' does not exist in the configuration file.",
                severity=StdoutSeverity.ERROR,
            )
        else:
            self.stdout(value)
            self.stdout(
                value,
                stdout_type=StdoutType.MACHINE_READABLE,
            )

    def _show_config(self) -> None:
        self.stdout(self._settings.pretty())
        self.stdout(
            self._settings.get_content(),
            stdout_type=StdoutType.MACHINE_READABLE,
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
