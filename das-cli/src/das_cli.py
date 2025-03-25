from injector import Injector

from commands.attention_broker import AttentionBrokerModule
from commands.config import ConfigModule
from commands.das import DasModule
from commands.db import DbModule
from commands.dbms_adapter import DbmsAdapterModule
from commands.example import ExampleModule
from commands.faas import FaaSModule
from commands.jupyter_notebook import JupyterNotebookModule
from commands.link_creation_agent import LinkCreationAgentModule
from commands.logs import LogsModule
from commands.metta import MettaModule
from commands.python_library import PythonLibraryModule
from commands.query_agent import QueryAgentModule
from commands.release_notes import ReleaseNotesModule
from commands.inference_agent import InferenceAgentModule

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
    DbmsAdapterModule,
    AttentionBrokerModule,
    QueryAgentModule,
    LinkCreationAgentModule,
    InferenceAgentModule,
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
