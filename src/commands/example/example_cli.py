from injector import inject
from common import Command, CommandGroup


class ExampleLocal(Command):
    name = "local"

    short_help = "Echo commands for local setup."

    help = """
'das-cli example local' displays an example of the initial steps required to run DAS locally on your server.

.SH EXAMPLES

Display an example of initial steps to run DAS locally.

$ das-cli example local
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
'das-cli example faas' displays an example of the initial steps required to connect to OpenFaaS functions using DAS.

.SH EXAMPLES

Display an example of initial steps to connect to OpenFaaS functions.

$ das-cli example faas
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

    short_help = "'das-cli example' offers a step-by-step guide for using DAS."

    help = """
'das-cli example' offers a step-by-step guide for using DAS.

This command provides various topics to choose from, each offering a step-by-step guide to help you set up and configure DAS for different scenarios, such as local, connecting to OpenFaaS functions, and more.
"""

    @inject
    def __init__(self, example_local: ExampleLocal, example_faas: ExampleFaaS) -> None:
        super().__init__()
        self.add_commands(
            [
                example_local.command,
                example_faas.command,
            ]
        )
