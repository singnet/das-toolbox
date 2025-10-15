import json
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Callable, Dict, List

import click
import yaml
from fabric import Connection

from common import Choice
from common.utils import log_exception


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
    ]

    default_params = [
        CommandOption(
            ["--output-format", "-o"],
            type=Choice(["plain", "json", "yaml"]),
            help="Choose the output format: plain, json, yaml",
            required=False,
            default="plain",
        ),
    ]

    remote_params = [
        CommandOption(
            ["--remote"],
            type=bool,
            default=False,
            is_flag=True,
            help="whether to run the command on a remote server",
        ),
        CommandOption(
            ["--host", "-H"],
            type=str,
            help="the login user for the remote connection",
            required=False,
        ),
        CommandOption(
            ["--user", "-H"],
            type=str,
            help="the login user for the remote connection",
            required=False,
        ),
        CommandOption(
            ["--port", "-H"],
            type=int,
            help="the remote port",
            required=False,
        ),
        CommandOption(
            ["--key-file"],
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
            ["--connect-timeout"],
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
        self.command = click.Command(
            name=self.name,
            callback=self.safe_run,
            help=self.help,
            short_help=self.short_help,
            params=self.params + self.remote_params + self.default_params,
        )

    def _get_remote_execution_context(self):
        """ Reads remote execution configuration from Click context.
        Returns ExecutionContext or None if not remote.
        """
        ctx = click.get_current_context(silent=True)

        if not ctx or not ctx.obj or "execution_context" not in ctx.obj:
            return None

        execution_context = ctx.obj["execution_context"]

        if not execution_context.is_remote():
            return None

        return execution_context

    def _get_remote_kwargs_from_context(self) -> tuple[bool, dict]:
        """
        Reads remote execution configuration from Click context.
        Returns (remote_enabled, remote_kwargs)
        """
        execution_context = self._get_remote_execution_context()

        if execution_context is None:
            return (False, {})

        connection = getattr(execution_context, "connection", {})
        connect_kwargs = {}
        if connection.get("remote_key_path"):
            connect_kwargs["key_filename"] = connection["remote_key_path"]
        if connection.get("remote_password"):
            connect_kwargs["password"] = connection["remote_password"]

        remote_kwargs = {
            "user": connection.get("remote_user", ""),
            "port": connection.get("remote_port", 22),
            "host": connection.get("remote_host", ""),
            "connect_kwargs": connect_kwargs,
            "connect_timeout": connection.get("connect_timeout", 10),
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

    def _remote_run(self, kwargs, remote_kwargs):
        ctx = click.get_current_context()
        prefix = "das-cli"
        command_path = " ".join(ctx.command_path.split(" ")[1:])
        extra_args = self._dict_to_command_line_args(kwargs)
        execution_context = self._get_remote_execution_context()
        remote_context = execution_context.context and f'--context \'{execution_context.context}\'' or ''

        command = f"{prefix} {command_path} {extra_args} {remote_context}".strip()
        print(command)
        Connection(**remote_kwargs).run(command)

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

    def prompt(
        self,
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

    def confirm(self, text: str, **kwarg):
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
