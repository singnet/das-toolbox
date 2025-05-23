from enum import Enum
from typing import Any, List

import click
from fabric import Connection

from common.logger import logger


class StdoutType(Enum):
    DEFAULT = "default"


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

    def __init__(self) -> None:
        self.command = click.Command(
            name=self.name,
            callback=self.safe_run,
            help=self.help,
            short_help=self.short_help,
            params=self.params + self.remote_params,
        )

    def _get_remote_kwargs(self, kwargs) -> tuple[bool, dict, dict]:
        """
        Gets remote kwargs from kwargs.
        Params:
        Returns (bool, kwargs, remote_kwargs):
            First value is whether the command should be run on a remote server or not.
        """
        if not kwargs:
            return (False, kwargs, {})
        remote_kwargs = {
            "user": kwargs.pop("user", ""),
            "port": kwargs.pop("port", 22),
            "host": kwargs.pop("host", ""),
            "connect_kwargs": {
                "key_filename": kwargs.pop("key_file", None),
                "password": kwargs.pop("password", None),
            },
            "connect_timeout": kwargs.pop("connect_timeout", 10),
        }
        remote = kwargs.pop("remote", False)

        return (remote, kwargs, remote_kwargs)

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
        command = f"{prefix} {command_path} {extra_args}"
        Connection(**remote_kwargs).run(command)

    def safe_run(self, **kwargs):
        remote, kwargs, remote_kwargs = self._get_remote_kwargs(kwargs)
        try:
            if remote:
                return self._remote_run(kwargs, remote_kwargs)
            return self.run(**kwargs)
        except Exception as e:
            error_type = e.__class__.__name__
            error_message = str(e)
            pretty_message = f"\033[31m[{error_type}] {error_message}\033[39m"

            logger().exception(error_message)

            print(pretty_message)

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

    @staticmethod
    def stdout(
        content: Any,
        stdout_type: StdoutType = StdoutType.DEFAULT,
        severity: StdoutSeverity = StdoutSeverity.INFO,
        new_line: bool = True,
    ) -> None:
        message = content
        logger_instance = {
            StdoutSeverity.ERROR: logger().error,
            StdoutSeverity.INFO: logger().info,
            StdoutSeverity.SUCCESS: logger().info,
            StdoutSeverity.WARNING: logger().warning,
        }
        log = logger_instance[severity]

        if stdout_type == StdoutType.DEFAULT:
            click.secho(message, fg=severity.value, nl=new_line)

        log(message)

    def run(self, *args, **kwargs):
        raise NotImplementedError(
            f"The 'run' method from the command '{self.name}' should be implemented."
        )


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

    def add_commands(self, commands: list):
        for command in commands:
            self.group.add_command(command)

    def configure_params(self):
        for param in self.params:
            self.group.params.append(param)
