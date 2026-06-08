from typing import Any

from common import IntRange
from common.command import Command, StdoutSeverity
from common.docker.remote_context_manager import RemoteContextManager, Server
from common.network import get_public_ip
from common.prompt_types import ReachableIpAddress, ValidUsername
from common.settings import Settings
from common.utils import extract_service_port, get_rand_token, get_server_username
from common.prompt_types import AbsolutePath

from .setup_utils import get_default_value


BACKEND_OPTIONS = {
    "MongoDB + Redis": "redismongodb",
    "MongoDB + MorkDB": "morkdb",
    "InMemoryDB": "inmemorydb",
}

ATOMDB_OPTIONS = {
    **BACKEND_OPTIONS,
    "RemoteDB": "remotedb",
    "AdapterDB": "adapterdb",
}


# Nodes setup

def build_localhost_node() -> dict[str, Any]:
    return {
        "context": "default",
        **Server(
            {
                "ip": "localhost",
                "username": get_server_username(),
            }
        ),
    }


def build_node(port: int) -> dict[str, Any]:
    remote_context_manager = RemoteContextManager()

    username = Command.prompt(
        "Enter the SSH username for the node:",
        type=ValidUsername(),
        default=get_server_username(),
    )

    ip = Command.prompt(
        "Enter the IP address of the node:",
        type=ReachableIpAddress(username, port),
        default=get_public_ip(),
    )

    server = Server(
        {
            "ip": ip,
            "username": username,
        }
    )

    docker_context = remote_context_manager.create_servers_context([server])

    return {
        "context": docker_context[0]["context"],
        **server,
    }


def setup_nodes(port: int) -> list[dict[str, Any]]:

    nodes: list[dict[str, Any]] = []
    min_nodes = 3

    join_current_server = Command.confirm(
        "Do you want to join the current server as an actual node on the network?",
        default=True,
    )

    if join_current_server:
        nodes.append(build_localhost_node())
        min_nodes -= 1

    total_nodes = Command.prompt(
        f"Enter the total number of nodes for the cluster (>= {min_nodes})",
        hide_input=False,
        type=IntRange(min_nodes),
        default=min_nodes,
    )

    for _ in range(total_nodes):
        nodes.append(build_node(port))

    return nodes


# MORK/MONGO/REDIS setup

def mongo_setup(settings: Settings, skip_cluster: bool) -> dict[str, Any]:

    mongodb_port = Command.prompt(
        "Enter the port for MongoDB:",
        default=extract_service_port(
            str(get_default_value(settings, "atomdb.mongodb.endpoint"))
        ),
        type=int,
    )

    mongodb_username = Command.prompt(
        "Enter MongoDB username",
        default=get_default_value(settings, "atomdb.mongodb.username"),
    )

    mongodb_password = Command.prompt(
        "Enter MongoDB password",
        default=get_default_value(settings, "atomdb.mongodb.password"),
    )

    mongodb_cluster = (
        False
        if skip_cluster
        else Command.confirm(
            "Do you want to set up MongoDB as a cluster?",
            default=False,
        )
    )

    mongodb_nodes = (
        setup_nodes(mongodb_port)
        if mongodb_cluster
        else [build_localhost_node()]
    )

    cluster_secret_key = (
        get_rand_token(num_bytes=15)
        if mongodb_cluster
        else "None"
    )

    return {
        "mongodb": {
            "endpoint": f"localhost:{mongodb_port}",
            "username": mongodb_username,
            "password": mongodb_password,
            "cluster": mongodb_cluster,
            "cluster_secret_key": cluster_secret_key,
            "nodes": mongodb_nodes,
        }
    }


def redis_setup(
    settings: Settings,
    skip_cluster: bool = False,
) -> dict[str, Any]:

    redis_port = Command.prompt(
        "Enter the port for Redis:",
        default=extract_service_port(
            str(get_default_value(settings, "atomdb.redis.endpoint"))
        ),
        type=int,
    )

    redis_cluster = (
        False
        if skip_cluster
        else Command.confirm(
            "Do you want to set up Redis as a cluster?",
            default=False,
        )
    )

    redis_nodes = (
        setup_nodes(redis_port)
        if redis_cluster
        else [build_localhost_node()]
    )

    return {
        "redis": {
            "endpoint": f"localhost:{redis_port}",
            "cluster": redis_cluster,
            "nodes": redis_nodes,
        }
    }


def mork_setup(settings: Settings) -> dict[str, Any]:

    morkdb_port = Command.prompt(
        "Enter the port for MorkDB:",
        default=extract_service_port(
            str(get_default_value(settings, "atomdb.morkdb.endpoint"))
        ),
    )

    return {
        "morkdb": {
            "endpoint": f"localhost:{morkdb_port}",
        }
    }


# RemoteDB setup

def build_backend_config(
    backend_type: str,
    settings: Settings,
    *,
    skip_cluster: bool,
) -> dict[str, Any]:
    match backend_type:
        case "redismongodb":
            return {
                **mongo_setup(settings, skip_cluster),
                **redis_setup(settings, skip_cluster),
            }

        case "morkdb":
            return {
                **mongo_setup(settings, skip_cluster),
                **mork_setup(settings),
            }

        case "inmemorydb":
            return {}

        case _:
            return {}


def build_local_persistence(
    settings: Settings,
    base_name: str,
) -> dict[str, Any]:
    persistence_type = Command.select(
        "Select local persistence type",
        options=BACKEND_OPTIONS,
        default="morkdb",
    )

    return {
        "type": persistence_type,
        "context": f"{base_name}_local_",
        **build_backend_config(
            persistence_type,
            settings,
            skip_cluster=True,
        ),
    }

def setup_peer(
    settings: Settings,
    peer_index: int,
) -> dict[str, Any]:

    backend_type = Command.select(
        "Select the Remote peer backend type",
        options=BACKEND_OPTIONS,
        default="redismongodb",
    )

    peer_name = f"peer{peer_index + 1}"
    context_prefix = f"remotedb_{peer_name}"

    peer = {
        "uid": peer_name,
        "type": backend_type,
        "context": f"{context_prefix}_",
        **build_backend_config(
            backend_type,
            settings,
            skip_cluster=True,
        ),
    }

    peer["local_persistence"] = build_local_persistence(
        settings,
        context_prefix,
    )

    return peer


def remotedb_setup(settings: Settings) -> dict[str, Any]:

    peer_count = Command.prompt(
        "How many remoteDB Peers would you like to add?",
        type=IntRange(1),
        default=1,
    )

    return {
        "remote_peers": [
            setup_peer(settings, i)
            for i in range(peer_count)
        ]
    }


# AdapterDB setup

def setup_context_mapping_paths() -> list[str]:
    context_mapping_paths = []
    addMorePaths = True
    
    while addMorePaths:

        context_path = Command.prompt(
            "Enter the absolute path to one or more context mapping files (separated by comma)", 
            type=AbsolutePath(
                dir_okay=False,
                file_okay=True,
                exists=True,
                writable=True,
                readable=True,
            )
        )

        addMorePaths = Command.confirm("Add more context paths?", default=False)

        context_mapping_paths.append(context_path)

    return context_mapping_paths

def setup_output_directory() -> str:
    
    context_path = Command.prompt(
        "Enter the absolute path to where the metta files will be outputted", 
        type=AbsolutePath(
            dir_okay=True,
            file_okay=False,
            exists=True,
            writable=True,
            readable=True,
        )
    )

    return context_path

def adapterdb_setup(settings: Settings) -> dict[str, Any]:

    adapter_port = Command.prompt("Enter the AdapterDB port:", default=40023, type=int)
    database_type = Command.select("Select source database type", options={"PostgreSQL": "postgres", }, default="postgres")
    host = Command.prompt("Database host", default="remote.database.org")
    port = Command.prompt("Database port",default=5432,type=int)
    username = Command.prompt("Database username", default="admin")
    password = Command.prompt("Database password", default="admin")
    database = Command.prompt("Database name", default="database")
    context_mappings = setup_context_mapping_paths()
    export_metta = Command.confirm("Export mapped MeTTa files?", default=True)
    metta_output_dir = setup_output_directory() if export_metta else None

    reuse_mongodb = Command.confirm(
        "Reuse AdapterDB MongoDB persistence?",
        default=True,
    )

    backend_type = Command.select(
        "Select AtomDB backend for AdapterDB",
        options=BACKEND_OPTIONS,
        default="redismongodb",
    )

    atomdb_backend = {
        "type": backend_type,
        **build_backend_config(
            backend_type,
            settings,
            skip_cluster=False,
        ),
    }

    return {
        "adapterdb": {
            "endpoint": f"localhost:{adapter_port}",
            "type": database_type,
            "database_credentials": {
                "host": host,
                "port": port,
                "username": username,
                "password": password,
                "database": database,
            },
            "context_mapping_paths": context_mappings,
            "export_metta_on_mapping": {
                "enabled": export_metta,
                "output_dir": metta_output_dir,
            },
            "persistence": {
                "reuse_mongodb": reuse_mongodb,
            },
            "atomdb_backend": atomdb_backend,
        }
    }


# AtomDB section

def atomdb_config_section(settings: Settings) -> dict[str, Any]:
    atomdb_type = Command.select(
        "Select the AtomDB backend type",
        options=ATOMDB_OPTIONS,
        default="redismongodb",
    )

    atomdb_config: dict[str, Any] = {
        "type": atomdb_type,
    }

    match atomdb_type:
        case "remotedb":
            atomdb_config.update(remotedb_setup(settings))

        case "adapterdb":
            atomdb_config.update(adapterdb_setup(settings))

        case _:
            atomdb_config.update(
                build_backend_config(
                    atomdb_type,
                    settings,
                    skip_cluster=False,
                )
            )

    return {
        "atomdb": atomdb_config,
    }