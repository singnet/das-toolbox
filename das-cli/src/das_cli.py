from injector import Injector

from commands.attention_broker import AttentionBrokerModule
from commands.config import ConfigModule
from commands.context_broker import ContextBrokerModule
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

import sys
from common.execution_context import ExecutionContext

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
    ContextBrokerModule,
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


def build_execution_context_from_argv(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    def get_arg_value(name, default=None):
        if name in argv:
            idx = argv.index(name)
            if idx + 1 < len(argv):
                return argv[idx + 1]
        return default

    remote_host = get_arg_value("--host")
    remote_port = int(get_arg_value("--port", 22))
    remote_user = get_arg_value("--user")
    client_username = get_arg_value("--client-username")
    context_json = get_arg_value("--context")

    return ExecutionContext(
        connection={
            "remote_host": remote_host,
            "remote_port": remote_port,
            "remote_user": remote_user,
            "client_username": client_username,
        },
        context_str=context_json,
    )

def init_cli(module):
    try:
        m = module()
        container = Injector([m])
        instance = container.get(m.get_instance())

        exec_ctx = build_execution_context_from_argv()
        if not hasattr(instance.group, "obj"):
            instance.group.obj = {}
        instance.group.obj["execution_context"] = exec_ctx

        return instance.group
    except Exception as e:
        log_exception(e)
        exit(1)


das_cli = init_cli(DasModule)
init_modules(das_cli)

if __name__ == "__main__":
    das_cli()
