import json
import sys
from contextlib import suppress
from enum import Enum
from typing import List, Optional, TypedDict, Union

import click
import yaml
from fabric import Connection
from InquirerPy import inquirer
from InquirerPy.base.control import Choice as InquirerChoice
from invoke.exceptions import UnexpectedExit

from common import Choice
from common.exceptions import InvalidRemoteConfiguration
from common.execution_context import ExecutionContext, SSHParams
from common.prompt_types import ValidUsername
from common.service_response import ServiceResponse, StdoutStatus
from common.utils import log_exception
from settings.config import SECRETS_PATH

from .utils import env_to_dict


class SelectOption(TypedDict):
    name: str
    value: str


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


class Command:
    name = "unknown"
    help = ""
    short_help = ""
    params: List = []
    aliases: List[str] = []

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
            is_eager=True,
            help="Whether to run the command on a remote server",
        ),
        CommandOption(
            ["--host", "-h"],
            type=str,
            is_eager=True,
            help="Remote host to connect to",
            required=False,
        ),
        CommandOption(
            ["--user", "-u"],
            type=ValidUsername(),
            is_eager=True,
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
        if hasattr(self, "_output_format") and self._output_format is not None:
            return self._output_format
        ctx = click.get_current_context(silent=True)
        if ctx:
            return ctx.params.get("output_format", "plain")
        return "plain"

    def __init__(self) -> None:
        self._execution_context: Optional[ExecutionContext] = None
        self._structured_error_emitted = False
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
        positional_args = []
        optional_args = []

        positional_names = {p.name for p in self.params if isinstance(p, CommandArgument)}

        for key, value in d.items():
            if value is None:
                continue

            if key in positional_names:
                positional_args.append(str(value))
                continue

            arg_key = str(key).replace("_", "-")
            if isinstance(value, bool):
                if value:
                    optional_args.append(f"--{arg_key}")
            else:
                optional_args.append(f"--{arg_key} {str(value)}")

        return " ".join(positional_args + optional_args)

    def _get_clean_command(self) -> str:
        ctx = click.get_current_context(silent=True)
        if ctx:
            path = ctx.command_path
            if path.startswith("das-cli "):
                path = path[len("das-cli ") :]
            return path.strip()
        return self.name

    def get_execution_context(self) -> ExecutionContext:
        ctx = click.get_current_context()
        if not self._execution_context:
            cli_options = ctx.params if ctx else {}
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
        REMOTE_SECRETS_PATH = "$HOME/.das/.env"

        try:
            env_dict = env_to_dict(SECRETS_PATH)
            config_path = env_dict.get("configpath")
            with open(config_path, "r") as f:
                local_config = json.loads(f.read())
        except Exception as e:
            raise FileNotFoundError(
                f"The local configuration file contains errors or is missing content. "
                f"Verify your configuration settings and try again. Details: {e}"
            )

        try:
            command = f"grep 'configpath' {REMOTE_SECRETS_PATH} | cut -d'=' -f2 | xargs cat"
            result = Connection(**remote_kwargs).run(command, hide=True)
            remote_config = json.loads(result.stdout)
        except UnexpectedExit:
            raise FileNotFoundError(f"Remote configuration file not found at {REMOTE_SECRETS_PATH}")
        except Exception as e:
            raise InvalidRemoteConfiguration(
                f"Failed to fetch and parse remote configuration due to a connection/authentication error via SSH. Exception: {e}"
            )

        if local_config == remote_config:
            return
        else:
            raise InvalidRemoteConfiguration(
                "Remote configuration file does not match the local configuration file."
            )

    def _echo_remote_streams(self, result) -> None:
        if result.stdout:
            click.echo(result.stdout, nl=False)
            if not result.stdout.endswith("\n"):
                click.echo()
        if result.stderr:
            click.echo(result.stderr, nl=False, err=True)
            if not result.stderr.endswith("\n"):
                click.echo(err=True)

    @staticmethod
    def _remote_das_cli_missing(result) -> bool:
        combined = f"{result.stdout or ''}\n{result.stderr or ''}".lower()
        if "das-cli" not in combined and "das_cli" not in combined:
            return False

        return (
            "command not found" in combined
            or "no such file or directory" in combined
        )

    def _remote_run(self, kwargs, remote_kwargs):
        prefix = "das-cli"

        output_fmt = getattr(self, "_output_format", "plain")
        if output_fmt and output_fmt != "plain":
            kwargs["output_format"] = output_fmt

        stream_val = getattr(self, "_stream", None)
        if stream_val:
            kwargs["stream"] = stream_val

        extra_args = self._dict_to_command_line_args(kwargs)
        execution_context = self._get_remote_execution_context()
        context_encoded = execution_context.to_str(include_ssh=False)
        command_path = execution_context.command_path
        remote_context = f"--context '{context_encoded}'"
        command = f"{prefix} {command_path} {extra_args} {remote_context}".strip()

        try:
            if "config" not in command_path:
                self._check_remote_config(remote_kwargs)

            result = Connection(**remote_kwargs).run(command, hide=True, warn=True)
            self._echo_remote_streams(result)

            if result.failed:
                if self._remote_das_cli_missing(result):
                    self.stdout(
                        "[ERROR] das-cli is missing on the remote machine. Verify the installation.",
                        severity=StdoutSeverity.ERROR,
                    )
                raise UnexpectedExit(result)

        except UnexpectedExit:
            raise
        except Exception as e:
            self.stdout(f"[ERROR] {e}", severity=StdoutSeverity.ERROR)
            raise

    def safe_run(self, **kwargs):
        remote, remote_kwargs = self._get_remote_kwargs_from_context()
        self._structured_error_emitted = False
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
            raise click.exceptions.Exit(1)

        if not remote:
            self.flush_stdout()
            if self._structured_error_emitted:
                raise click.exceptions.Exit(1)

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

    @staticmethod
    def _payload_indicates_error(payload: dict) -> bool:
        status = payload.get("status")
        if isinstance(status, StdoutStatus):
            return status == StdoutStatus.ERROR
        if status is None:
            return False
        return str(status).lower() == StdoutStatus.ERROR.value

    def _handle_output(self, output_object, severity, new_line):
        if isinstance(output_object, dict):
            payload = output_object
            message = payload.get("message", str(payload))
        else:
            payload = dict(output_object)
            message = output_object.message

        if self._payload_indicates_error(payload):
            self._structured_error_emitted = True

        if self.output_format == "plain":
            self._print_colored(message, severity, new_line)

        elif self.output_format == "json":
            click.echo(json.dumps(payload), nl=True)
            sys.stdout.flush()

        elif self.output_format == "yaml":
            click.echo(yaml.dump(payload, sort_keys=False), nl=False)
            sys.stdout.flush()

    def log(self, message: str, severity: StdoutSeverity = StdoutSeverity.INFO) -> None:
        self._print_colored(message, severity, new_line=True, err=True)

    def stdout(
        self,
        content: Union[str, ServiceResponse, dict],
        severity: StdoutSeverity = StdoutSeverity.INFO,
        new_line: bool = True,
    ) -> None:
        if isinstance(content, str):
            if self.output_format == "plain":
                self._print_colored(content, severity, new_line)
            return

        self._handle_output(content, severity, new_line)

    def flush_stdout(self):
        pass

    def run(self, *args, **kwargs):
        raise NotImplementedError(
            f"The 'run' method from the command '{self.name}' should be implemented."
        )

    def _print_colored(
        self,
        text: str,
        severity: StdoutSeverity,
        new_line: bool = True,
        *,
        err: bool = False,
    ) -> None:
        fg_map = {
            StdoutSeverity.SUCCESS: "green",
            StdoutSeverity.ERROR: "red",
            StdoutSeverity.WARNING: "yellow",
        }
        fg = fg_map.get(severity)
        if fg:
            click.secho(text, fg=fg, nl=new_line, err=err)
        else:
            click.echo(text, nl=new_line, err=err)


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
