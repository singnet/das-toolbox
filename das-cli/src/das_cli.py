from injector import Injector

from commands.attention_broker import AttentionBrokerModule
from commands.config import ConfigModule
from commands.das import DasModule
from commands.db import DbModule
from commands.dbms_adapter import DbmsAdapterModule
from commands.evolution_agent import EvolutionAgentModule
from commands.example import ExampleModule
from commands.inference_agent import InferenceAgentModule
from commands.jupyter_notebook import JupyterNotebookModule
from commands.link_creation_agent import LinkCreationAgentModule
from commands.logs import LogsModule
from commands.metta import MettaModule
from commands.python_library import PythonLibraryModule
from commands.query_agent import QueryAgentModule
from commands.release_notes import ReleaseNotesModule
from common.docker.docker_network_manager import init_network
from common.utils import log_exception

MODULES = [
    ConfigModule,
    ExampleModule,
    DbModule,
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
    EvolutionAgentModule,
]


def bootstrap():
    init_network()


def init_module(cli, module):
    m = module()
    container = Injector([m])
    instance = container.get(m.get_instance())
    cli.add_command(instance.group)

    for alias in getattr(instance, "aliases", []):
        cli.add_command(instance.group, name=alias)


def init_modules(cli):
    try:
        bootstrap()
        for module in MODULES:
            init_module(cli, module)
    except Exception as e:
        log_exception(e)
        exit(1)


def init_cli(module):
    try:
        m = module()
        container = Injector([m])
        instance = container.get(m.get_instance())

        return instance.group
    except Exception as e:
        log_exception(e)
        exit(1)


das_cli = init_cli(DasModule)
init_modules(das_cli)

if __name__ == "__main__":
    das_cli()
