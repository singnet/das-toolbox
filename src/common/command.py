import click
from typing import Any
from enum import Enum
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

    def __init__(self) -> None:
        self.command = click.Command(
            name=self.name,
            callback=self.run,
            help=self.help,
            short_help=self.short_help,
            params=self.params,
        )

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
    params = []

    def __init__(self) -> None:
        self.group = click.Group(self.name)
        self.configure_params()

    def add_commands(self, commands: list):
        for command in commands:
            self.group.add_command(command)

    def configure_params(self):
        for param in self.params:
            self.group.params.append(param)
