from fabric import Connection
from enum import Enum
from typing import Any

import click

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
    params = []
    remote_params = [
        CommandOption(["--remote/--no-remote"], type=bool, default=False),
        CommandOption(["--host", "-H"], type=str, help="qwer", required=False),
        CommandOption(["--user", "-H"], type=str, help="qwer", required=False),
        CommandOption(["--port", "-H"], type=str, help="qwer", required=False),
    ]

    def __init__(self) -> None:
        self.command = click.Command(
            name=self.name,
            callback=self.safe_run,
            help=self.help,
            short_help=self.short_help,
            params=self.params + self.remote_params,
        )

    def _get_remote_kwargs(self, kwargs) -> tuple[dict, dict]:
        if not kwargs:
            return kwargs, {}
        remote_kwargs = {
            "user": kwargs.pop("user") or "",
            "port": kwargs.pop("port") or 22,
            "host": kwargs.pop("host") or "",
        }

        if not kwargs.pop("remote"):
            return kwargs, {}

        return (kwargs, remote_kwargs)

    def _remote_run(self, kwargs, remote_kwargs):

        try:
            ctx = click.get_current_context()
            command = ctx.command_path
            print(f"Executing remote {command=}...")
            result = Connection(**remote_kwargs).run(command)
            print(result)
        except Exception as e:
            print("Caught it")
            print(type(e))

    def safe_run(self, **kwargs):
        kwargs, remote_kwargs = self._get_remote_kwargs(kwargs)
        try:
            if remote_kwargs.get("host"):
                print(remote_kwargs)
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

    def stdout(
        self,
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

    def run(self):
        raise NotImplementedError(
            f"The 'run' method from the command '{self.name}' should be implemented."
        )


class CommandGroup(Command):
    name = "unknown"
    help = ""
    short_help = ""
    params = [
        CommandOption(["--hostGroup"], type=str, help="qwer", required=False),
    ]

    def __init__(self) -> None:
        self.group = click.Group(self.name)
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
