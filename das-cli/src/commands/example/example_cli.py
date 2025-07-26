from injector import inject

from common import Command, CommandGroup, StdoutType


class ExampleLocal(Command):
    name = "local"

    short_help = "Echo commands for local setup."

    help = """
NAME

    das-cli example local - Example commands for running DAS locally.

SYNOPSIS

    das-cli example local

DESCRIPTION

    Displays an example of the initial steps required to run DAS locally on your server.

EXAMPLES

    Display example commands to set up DAS locally:

        das-cli example local
"""

    def __init__(self, script_name) -> None:
        super().__init__()
        self._script_name = script_name

    def run(self):
        output = f"""
# Set the configuration file
{self._script_name} config set

# Start server services
{self._script_name} db start

# Validate a Metta file or directory
{self._script_name} metta check <metta file path>

# Load Metta files
{self._script_name} metta load <metta file path>
"""
        self.stdout(output)
        self.stdout(
            {
                "configuration": {
                    "description": "Set the configuration file",
                    "command": f"{self._script_name} config set",
                },
                "services": {
                    "description": "Start server services",
                    "command": f"{self._script_name} db start",
                },
                "metta_check": {
                    "description": "Validate a Metta file or directory",
                    "command": f"{self._script_name} metta check <metta file path>",
                },
                "metta_load": {
                    "description": "Load Metta files",
                    "command": f"{self._script_name} metta load <metta file path",
                },
            },
            stdout_type=StdoutType.MACHINE_READABLE,
        )


class ExampleCli(CommandGroup):
    name = "example"

    aliases = ["ex"]

    short_help = "'das-cli example' offers a step-by-step guide for using DAS."

    help = """
NAME

    das-cli example - Step-by-step example commands for using DAS.

SYNOPSIS

    das-cli example <command>

DESCRIPTION

    'das-cli example' provides step-by-step guides for various DAS usage scenarios.
    You can choose topics such as 'local' for running DAS locally, or 'faas' for
    connecting to OpenFaaS functions.

SUBCOMMANDS

    local       Shows example commands for local DAS setup.
    faas        Shows example commands for OpenFaaS setup.

EXAMPLES

    Display help for example commands:

        das-cli example --help

    Display local setup example:

        das-cli example local
"""

    @inject
    def __init__(self, example_local: ExampleLocal) -> None:
        super().__init__()
        self.add_commands(
            [
                example_local,
            ]
        )
