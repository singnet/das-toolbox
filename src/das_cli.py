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


das_cli = init_cli(DasModule)
init_modules(das_cli)

if __name__ == "__main__":
    das_cli()
