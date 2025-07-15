from injector import inject

from common import Command, CommandGroup


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
# Install Hyperon-DAS:
pip3 install hyperon-das

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


class ExampleFaaS(Command):
    name = "faas"

    short_help = "Echo commands for OpenFaaS setup."

    help = """
NAME

    das-cli example faas - Example commands for connecting to OpenFaaS functions.

SYNOPSIS

    das-cli example faas

DESCRIPTION

    Displays an example of the initial steps required to connect to OpenFaaS functions using DAS.

EXAMPLES

    Display example commands to set up DAS with OpenFaaS functions:

        das-cli example faas
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

# Start OpenFaaS Service
{self._script_name} faas start
"""
        self.stdout(output)


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

    Display OpenFaaS setup example:

        das-cli example faas
"""

    @inject
    def __init__(self, example_local: ExampleLocal, example_faas: ExampleFaaS) -> None:
        super().__init__()
        self.add_commands(
            [
                example_local,
                example_faas,
            ]
        )
