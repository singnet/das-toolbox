from injector import inject

from common import Command, CommandGroup, StdoutType

from .example_docs import HELP_EX_LOCAL, HELP_EXAMPLE, SHORT_HELP_EX_LOCAL, SHORT_HELP_EXAMPLE


class ExampleLocal(Command):
    name = "local"

    short_help = SHORT_HELP_EX_LOCAL

    help = HELP_EX_LOCAL

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

    short_help = SHORT_HELP_EXAMPLE

    help = HELP_EXAMPLE

    @inject
    def __init__(self, example_local: ExampleLocal) -> None:
        super().__init__()
        self.add_commands(
            [
                example_local,
            ]
        )
