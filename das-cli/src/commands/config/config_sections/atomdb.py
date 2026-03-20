from common.command import Command
from common.settings import Settings
from typing import Dict,Any
from typing import List
from common.utils import get_rand_token
from typing import Any, Dict, List
from common import IntRange
from common.docker.remote_context_manager import RemoteContextManager, Server
from common.prompt_types import ReachableIpAddress
from common.network import get_public_ip
from common.prompt_types import ValidUsername
from common.settings import Settings
from common.utils import get_rand_token, get_server_username
from common.network import get_public_ip
from .setup_utils import extract_port, get_default_value


#########################################
##          REDIS MONGO SETUP          ##
#########################################

def build_localhost_node() -> Dict[str, Any]:
    server_user = get_server_username()

    node = Server(
            {
                "ip": "localhost",
                "username": server_user,
            }
    )

    return {
        "context": "default",
        **node,
    }

def build_node(port:int) -> Dict[str, Any]:

    remote_context_manager = RemoteContextManager()

    username = Command.prompt(
        "Enter the SSH username for the node:",
        type=ValidUsername(),
        default=get_server_username(),
    )

    ip = Command.prompt(
        "Enter the IP address of the node:",
        type= ReachableIpAddress(username,port),
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

def setup_nodes(port:int) -> List[Dict[str, Any]]:
    nodes = []
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

    for i in range(0, total_nodes):
        nodes.append(build_node(port))

    return [*nodes]

def mongo_setup(settings: Settings, skip_cluster: bool) -> Dict[str, Any]:

    mongodb_port = Command.prompt(
        "Enter the port for MongoDB:",
        default=extract_port(get_default_value(settings, "atomdb.mongodb.endpoint")),
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

    mongodb_cluster = False if skip_cluster else Command.confirm(
        "Do you want to set up MongoDB as a cluster?",
        default=False
    )

    if mongodb_cluster:
        cluster_secret_key = get_rand_token(num_bytes=15)
        mongodb_nodes = setup_nodes(mongodb_port)

    return {
        "mongodb": {
            "endpoint": f"localhost:{mongodb_port}",
            "username": mongodb_username,
            "password": mongodb_password,
            "cluster": str(mongodb_cluster).lower(),
            "cluster_secret_key": cluster_secret_key if mongodb_cluster else "None",
            "nodes": mongodb_nodes if mongodb_cluster else []
        }
    }

def redis_setup(settings: Settings, skip_cluster: bool = False) -> Dict[str, Any]:

    redis_port = Command.prompt(
        "Enter the port for Redis:",
        default= extract_port(get_default_value(settings, "atomdb.redis.endpoint")),
        type=int,
    )

    redis_cluster = False if skip_cluster is True else Command.confirm(
        "Do you want to set up Redis as a cluster?",
        default=False
    )

    if redis_cluster:
        redis_nodes = setup_nodes(redis_port)

    return {
        "redis": {
            "endpoint": f"localhost:{redis_port}",
            "cluster": str(redis_cluster).lower(),
            "nodes": redis_nodes if redis_cluster else []
        }
    }

#########################################
##           MORK MONGO SETUP          ##
#########################################

def mork_setup(settings: Settings) -> Dict[str, Any]:

    morkdb_port = Command.prompt(
        "Enter the port for MorkDB:",
        default= extract_port(get_default_value(settings, "atomdb.morkdb.endpoint")),
        type=int,
    )

    return {
        "morkdb": {
            "endpoint": f"localhost:{morkdb_port}",
        }
    }

#########################################
##            REMOTEDB SETUP           ##
#########################################

def build_local_persistence(settings: Settings, base_name: str) -> Dict[str, Any]:

    persistence_type = Command.select(
        "Select local persistence type",
        options={
            "MongoDB + Redis": "redismongodb",
            "MongoDB + MorkDB": "morkmongodb",
            "InMemoryDB": "inmemorydb"
        },
        default="morkmongodb"
    )

    config = {
        "type": persistence_type,
        "context": f"{base_name}_local_"
    }

    match persistence_type:
        case "redismongodb":
            config.update(mongo_setup(settings, skip_cluster=True))
            config.update(redis_setup(settings, skip_cluster=True))
        case "morkmongodb":
            config.update(mongo_setup(settings, skip_cluster=True))
            config.update(mork_setup(settings))
        case "inmemorydb":
            pass

    return config


def setup_peer(settings: Settings, iteration_num: int) -> Dict[str, Any]:

    atomdb_type = Command.select(
        "Select the Remote peer backend type",
        options={
            "MongoDB + Redis": "redismongodb",
            "MongoDB + MorkDB": "morkmongodb",
            "InMemoryDB": "inmemorydb"
        },
        default="redismongodb",
    )

    base_name = f"remotedb_peer{iteration_num+1}"

    peer = {
        "uid": f"peer{iteration_num+1}",
        "type": atomdb_type,
        "context": f"{base_name}_"
    }

    match atomdb_type:
        case "redismongodb":
            peer.update(mongo_setup(settings, skip_cluster=True))
            peer.update(redis_setup(settings, skip_cluster=True))
        case "morkmongodb":
            peer.update(mongo_setup(settings, skip_cluster=True))
            peer.update(mork_setup(settings))
        case "inmemorydb":
            pass

    peer["local_persistence"] = build_local_persistence(settings, base_name)

    return peer


def remotedb_setup(settings: Settings) -> Dict[str, Any]:

    remote_peers = []

    rmt_peers = Command.prompt(
        "How many remoteDB Peers would you like to add?",
        type=IntRange(1),
        default=1
    )

    for i in range(0, rmt_peers):
        remote_peers.append(setup_peer(settings, i))

    return {
        "remote_peers": remote_peers
    }

##############################################
##              SETUP SECTIONS              ##
##############################################

## ATOMDB ##

def atomdb_config_section(settings: Settings):
    atomdb_config = dict()

    atomdb_type = Command.select(
        "Select the AtomDB backend type",
        options={
            "MongoDB + Redis": "redismongodb",
            "MongoDB + MorkDB": "morkmongodb",
            "InMemoryDB": "inmemorydb",
            "RemoteDB": "remotedb",
        },
        default="redismongodb",
    )

    match atomdb_type:
        case "redismongodb":
            atomdb_config.update({"type": "redismongodb"})
            atomdb_config.update(mongo_setup(settings, skip_cluster=False))
            atomdb_config.update(redis_setup(settings, skip_cluster=False))

        case "morkmongodb":
            atomdb_config.update({"type": "morkmongodb"})
            atomdb_config.update(mongo_setup(settings, skip_cluster=False))
            atomdb_config.update(mork_setup(settings))

        case "inmemorydb":
            atomdb_config.update({"type": "inmemorydb"})

        case "remotedb":
            atomdb_config.update({"type": "remotedb"})
            atomdb_config.update(remotedb_setup(settings))

    return  {
                "atomdb": atomdb_config,
            }