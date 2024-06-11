from injector import Injector
from commands.config import ConfigModule
from commands.example import ExampleModule
from commands.db import DbModule
from commands.faas import FaaSModule
from commands.jupyter_notebook import JupyterNotebookModule
from commands.python_library import PythonLibraryModule
from commands.release_notes import ReleaseNotesModule
from commands.logs import LogsModule
from commands.metta import MettaModule
from commands.das import DasModule
from common.logger import logger

MODULES = [
    ConfigModule,
    ExampleModule,
    DbModule,
    FaaSModule,
    JupyterNotebookModule,
    LogsModule,
    MettaModule,
    PythonLibraryModule,
    ReleaseNotesModule,
]


def init_module(cli, module):
    m = module()
    container = Injector([m])
    instance = container.get(m.get_instance())
    cli.add_command(instance.group)


def init_modules(cli):
    for module in MODULES:
        init_module(cli, module)


def init_cli(module):
    m = module()
    container = Injector([m])
    instance = container.get(m.get_instance())

    return instance.group


def das_cli():
    try:
        cli = init_cli(DasModule)
        init_modules(cli)
        cli()
    except Exception as e:
        error_type = e.__class__.__name__
        error_message = str(e)
        pretty_message = f"\033[31m[{error_type}] {error_message}\033[39m"

        logger().exception(error_message)

        print(pretty_message)


if __name__ == "__main__":
    das_cli()
