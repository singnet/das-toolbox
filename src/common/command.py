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
            callback=self.safe_run,
            help=self.help,
            short_help=self.short_help,
            params=self.params,
        )

    def safe_run(self, **kwarg):
        try:
            return self.run(**kwarg)
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
