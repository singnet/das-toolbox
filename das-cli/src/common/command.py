import json
import sys
from contextlib import suppress
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, TypedDict, cast

import click
import yaml
from fabric import Connection
from InquirerPy import inquirer
from InquirerPy.base.control import Choice as InquirerChoice
from invoke.exceptions import UnexpectedExit

from common import Choice
from common.exceptions import InvalidRemoteConfiguration
from common.execution_context import ExecutionContext, SSHParams
from common.utils import log_exception
from common.prompt_types import ValidUsername
from settings.config import SECRETS_PATH


class SelectOption(TypedDict):
    name: str
    value: str


class StdoutType(Enum):
    DEFAULT = "default"
    MACHINE_READABLE = "machine_readable"


class StdoutSeverity(Enum):
    ERROR = "red"
    WARNING = "yellow"
    SUCCESS = "green"
    INFO = None


class CommandOption(click.Option):
    def __init__(self, *args, **kwargs):
        self.name = kwargs.pop("name", "unknown")
        super().__init__(*args, **kwargs)


class CommandArgument(click.Argument):
    def __init__(self, *args, **kwargs):
        self.name = kwargs.pop("name", "unknown")
        super().__init__(*args, **kwargs)


@dataclass
class OutputBufferEntry:
    message: Any
    stdout_type: StdoutType = StdoutType.DEFAULT
    severity: StdoutSeverity = StdoutSeverity.INFO
    new_line: bool = True

    def to_dict(self) -> dict:
        return asdict(self)


class Command:
    name = "unknown"
    help = ""
    short_help = ""
    params: List = []
    aliases: List[str] = []
    _output_buffer: List[OutputBufferEntry] = []

    exclude_params = [
        "output_format",
        "remote",
        "host",
        "user",
        "port",
        "key_file",
        "password",
        "connect_timeout",
        "context",
    ]

    default_params = [
        CommandOption(
            ["--output-format", "-o"],
            type=Choice(["plain", "json", "yaml"]),
            help="Choose the output format: plain, json, yaml",
            required=False,
            default="plain",
        ),
        CommandOption(
            ["--context"],
            type=str,
            help="Serialized execution context (Base64 JSON)",
            required=False,
        ),
    ]

    remote_params = [
        CommandOption(
            ["--remote"],
            type=bool,
            default=False,
            is_flag=True,
            help="Whether to run the command on a remote server",
        ),
        CommandOption(
            ["--host", "-H"],
            type=str,
            help="Remote host to connect to",
            required=False,
        ),
        CommandOption(
            ["--user", "-u"],
            type=ValidUsername(),
            help="SSH username for the remote connection",
            required=False,
        ),
        CommandOption(
            ["--port", "-p"],
            type=int,
            help="Remote port (default: 22)",
            required=False,
        ),
        CommandOption(
            ["--key-file", "-k"],
            type=str,
            help="Path to the SSH private key file",
            required=False,
        ),
        CommandOption(
            ["--password"],
            type=str,
            help="Password for authentication",
            required=False,
        ),
        CommandOption(
            ["--connect-timeout", "-t"],
            type=int,
            help="Timeout for establishing the connection in seconds",
            required=False,
            default=10,
        ),
    ]

    @property
    def command_path(self) -> str:
        ctx = click.get_current_context(silent=True)

        if ctx is None:
            return self.name

        return ctx.command_path

    @property
    def output_format(self):
        ctx = click.get_current_context(silent=True)
        if ctx:
            return ctx.params.get("output_format", "plain")
        return "plain"

    def __init__(self) -> None:
        self._execution_context: Optional[ExecutionContext] = None
        self.command = click.Command(
            name=self.name,
            callback=self.safe_run,
            help=self.help,
            short_help=self.short_help,
            params=self.params + self.remote_params + self.default_params,
        )

    def _get_remote_execution_context(self):
        execution_context = self.get_execution_context()

        if not execution_context.is_remote():
            return None

        return execution_context

    def _get_remote_kwargs_from_context(self) -> tuple[bool, dict]:
        """
        Reads remote execution configuration from Click context.
        Returns a tuple: (remote_enabled, remote_kwargs)
        """
        execution_context = self._get_remote_execution_context()

        if not execution_context:
            return (False, {})

        ssh_params = execution_context.source.get("ssh_params", {})
        if not ssh_params.get("host"):
            return (False, {})

        connect_kwargs = {}
        if ssh_params.get("key_path"):
            connect_kwargs["key_filename"] = ssh_params["key_path"]
        if ssh_params.get("password"):
            connect_kwargs["password"] = ssh_params["password"]

        remote_kwargs = {
            "user": ssh_params.get("user", ""),
            "port": ssh_params.get("port", 22),
            "host": ssh_params["host"],
            "connect_kwargs": connect_kwargs,
            "connect_timeout": ssh_params.get("connection_timeout", 10),
        }

        return (True, remote_kwargs)

    def _dict_to_command_line_args(self, d: dict) -> str:
        """
        Convert dict to command line args

        Params:
            d (dict): the dict to be converted convert

        """
        args = []
        for key, value in d.items():
            arg_key = str(key).replace("_", "-")

            if isinstance(value, bool):
                if value:
                    args.append(f"--{arg_key}")
            else:
                if value:
                    arg_value = str(value).lower()
                    arg = f"--{arg_key} {arg_value}"
                    args.append(arg)

        return " ".join(args)

    def _parse_args_to_dict(self) -> Dict[str, Any]:
        args = sys.argv[1:]

        result: Dict[str, Any] = {}
        i = 0

        while i < len(args):
            arg = args[i]

            if arg.startswith("--"):
                key = arg[2:].replace("-", "_")

                if (i + 1 >= len(args)) or args[i + 1].startswith("--"):
                    result[key] = True
                else:
                    value = args[i + 1]
                    if value.isdigit():
                        value = cast(Any, int(value))
                    result[key] = value
                    i += 1
            i += 1

        return result

    def _get_clean_command(self) -> str:
        args = sys.argv[1:]
        global_options = [opt.opts[0] for opt in self.default_params + self.remote_params]

        cleaned_args = []
        skip_next = False
        for i, arg in enumerate(args):
            if skip_next:
                skip_next = False
                continue

            if any(arg.startswith(opt) for opt in global_options):
                if i + 1 < len(args) and not args[i + 1].startswith("--"):
                    skip_next = True
                continue

            cleaned_args.append(arg)

        return " ".join(cleaned_args)

    def get_execution_context(self) -> ExecutionContext:
        if not self._execution_context:
            cli_options = self._parse_args_to_dict()

            execution_context = None
            context_str = cli_options.get("context")
            if context_str:
                with suppress(Exception):
                    execution_context = ExecutionContext.from_str(context_str)

            if execution_context is None:
                ssh_params = None
                if cli_options.get("remote") or cli_options.get("host") or cli_options.get("user"):
                    ssh_params = SSHParams(
                        host=cli_options.get("host", ""),
                        port=cli_options.get("port", 22),
                        user=cli_options.get("user", ""),
                        password=cli_options.get("password", ""),
                        key_path=cli_options.get("key_file", ""),
                        connection_timeout=cli_options.get("connection_timeout", 10),
                    )

                command_path = self._get_clean_command()
                execution_context = ExecutionContext(
                    command_path=command_path,
                    ssh_params=ssh_params,
                )

            self._execution_context = execution_context

        return self._execution_context

    def _normalize_config(self, config: dict) -> dict:
        services = config.get("services", {})

        for service_name, service_data in services.items():
            if "nodes" in service_data:
                service_data.pop("nodes")

            if "cluster_secret_key" in service_data:
                service_data.pop("cluster_secret_key")

        if "database" in services:
            db = services["database"]
            keep = {"atomdb_backend": db.get("atomdb_backend")}
            services["database"] = keep

        return config

    def _check_remote_config(self, remote_kwargs):

        REMOTE_SECRETS_PATH = "$HOME/.das/config.json"

        try:
            raw_local_config = json.loads(SECRETS_PATH.read_text())
            local_config = self._normalize_config(raw_local_config)

        except Exception:
            raise FileNotFoundError(f"Local configuration file not found at {SECRETS_PATH}")

        try:
            result = Connection(**remote_kwargs).run(f"cat {REMOTE_SECRETS_PATH}", hide=True)
            raw_remote_config = json.loads(result.stdout)
            remote_config = self._normalize_config(raw_remote_config)

        except UnexpectedExit:
            raise FileNotFoundError(f"Remote configuration file not found at {REMOTE_SECRETS_PATH}")

        if local_config == remote_config:
            return
        else:
            raise InvalidRemoteConfiguration(
                "Remote configuration file does not match the local configuration file."
            )

    def _remote_run(self, kwargs, remote_kwargs):
        prefix = "das-cli"
        extra_args = self._dict_to_command_line_args(kwargs)
        execution_context = self._get_remote_execution_context()
        context_encoded = execution_context.to_str(include_ssh=False)
        command_path = execution_context.command_path
        remote_context = f"--context '{context_encoded}'"
        command = f"{prefix} {command_path} {extra_args} {remote_context}".strip()

        try:
            self._check_remote_config(remote_kwargs)
            Connection(**remote_kwargs).run(command)
        except UnexpectedExit:
            self.stdout(
                "[ERROR] das-cli is missing on the remote machine. Verify the installation.",
                severity=StdoutSeverity.ERROR,
            )
        except InvalidRemoteConfiguration as e:
            self.stdout(f"[ERROR] {e}", severity=StdoutSeverity.ERROR)
        except FileNotFoundError as e:
            self.stdout(f"[ERROR] {e}", severity=StdoutSeverity.ERROR)

    def safe_run(self, **kwargs):
        remote, remote_kwargs = self._get_remote_kwargs_from_context()

        for param in getattr(self, "exclude_params", []):
            setattr(self, f"_{param}", kwargs.pop(param, None))

        try:
            if remote:
                self._remote_run(kwargs, remote_kwargs)
            else:
                self.run(**kwargs)
        except Exception as e:
            log_exception(e)

        self.flush_stdout()

    @staticmethod
    def select(text: str, options: dict[str, str], default: Optional[str] = None) -> str:
        if not options:
            raise ValueError("No options provided")

        if not sys.stdin.isatty():
            first_value = next(iter(options.values()))

            if not first_value and default is not None:
                return default

            return first_value

        choices = [InquirerChoice(v, name=k) for k, v in options.items()]
        choice = inquirer.select(
            message=text,
            choices=choices,
            pointer="> ",
            default=default,
        ).execute()

        return choice

    @staticmethod
    def prompt(
        text,
        default=None,
        hide_input=False,
        confirmation_prompt=False,
        type=None,
        value_proc=None,
        prompt_suffix=": ",
        show_default=True,
        err=False,
        show_choices=True,
    ):
        return click.prompt(
            text,
            default,
            hide_input,
            confirmation_prompt,
            type,
            value_proc,
            prompt_suffix,
            show_default,
            err,
            show_choices,
        )

    @staticmethod
    def confirm(text: str, **kwarg):
        return click.confirm(text=text, **kwarg)

    def _handle_default_output(self, entry: OutputBufferEntry) -> None:
        if self.output_format == "plain":
            self._print_colored(entry.message, entry.severity, entry.new_line)

    def _handle_machine_readable_output(self, entry: OutputBufferEntry) -> None:
        if self.output_format != "plain":
            self._output_buffer.append(entry)

    def stdout(
        self,
        content: Any,
        stdout_type: StdoutType = StdoutType.DEFAULT,
        severity: StdoutSeverity = StdoutSeverity.INFO,
        new_line: bool = True,
    ) -> None:
        entry = OutputBufferEntry(
            message=content,
            stdout_type=stdout_type,
            severity=severity,
            new_line=new_line,
        )

        handlers: Dict[StdoutType, Callable[[OutputBufferEntry], None]] = {
            StdoutType.DEFAULT: self._handle_default_output,
            StdoutType.MACHINE_READABLE: self._handle_machine_readable_output,
        }

        handler = handlers.get(stdout_type, self._handle_default_output)
        handler(entry)

    def run(self, *args, **kwargs):
        raise NotImplementedError(
            f"The 'run' method from the command '{self.name}' should be implemented."
        )

    def _flush_default_output(self):
        for entry in self._output_buffer:
            if entry.stdout_type == StdoutType.DEFAULT:
                self._print_colored(entry.message, entry.severity)

    def flush_stdout(self):
        if self.output_format == "plain":
            self._flush_default_output()
        elif self.output_format in {"json", "yaml"}:
            self._flush_machine_readable_output()

        self._output_buffer.clear()

    def _flush_machine_readable_output(self):
        results = [
            entry.message
            for entry in self._output_buffer
            if entry.stdout_type == StdoutType.MACHINE_READABLE
        ]

        if not results:
            return

        if self.output_format == "json":
            click.echo(json.dumps(results, indent=2))
        elif self.output_format == "yaml":
            click.echo(yaml.dump(results, sort_keys=False))

    def _print_colored(self, text: str, severity: StdoutSeverity, new_line: bool = True) -> None:
        fg_map = {
            StdoutSeverity.SUCCESS: "green",
            StdoutSeverity.ERROR: "red",
            StdoutSeverity.WARNING: "yellow",
            StdoutSeverity.INFO: None,
        }
        fg = fg_map.get(severity)
        if fg:
            click.secho(text, fg=fg, nl=new_line)
        else:
            click.echo(text, nl=new_line)


class CommandGroup(Command):
    name: str = "unknown"
    help: str = ""
    short_help: str = ""
    params: List = []

    group: click.Group

    def __init__(self) -> None:
        super().__init__()
        self.group = click.Group(
            self.name,
            help=self.help,
            short_help=self.short_help,
        )
        self.configure_params()

    def override_group_command(self):
        self.group.invoke_without_command = True
        self.group.callback = self.safe_run
        self.group.no_args_is_help = False

    def add_groups(self, groups: list["CommandGroup"]):
        for group_instance in groups:
            self.group.add_command(
                group_instance.group,
                name=group_instance.name,
            )

            for alias in getattr(group_instance, "aliases", []):
                self.group.add_command(group_instance.group, name=alias)

    def add_commands(self, commands: List[Command]):
        for command in commands:
            self.group.add_command(command.command)

            for alias in getattr(command, "aliases", []):
                self.group.add_command(command.command, name=alias)

    def configure_params(self):
        for param in self.params:
            self.group.params.append(param)
