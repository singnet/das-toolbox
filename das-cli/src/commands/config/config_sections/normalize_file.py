import getpass
from typing import Any, Dict, List

from common.docker import RemoteContextManager
from common.docker.remote_context_manager import Server
from common.settings import Settings
from common.utils import get_rand_token


def normalize_servers(
    nodes: List[Dict[str, Any]], current_user: str, context_manager: RemoteContextManager
) -> List[Dict[str, Any]]:
    updated_nodes = []
    servers_to_create_context: List[Server] = []

    for node in nodes:
        username = node.get("username")
        context = node.get("context")
        ip = node.get("ip", "localhost")

        if context == "default":
            if not username or username in ["root", "default"]:
                node["username"] = current_user

            updated_nodes.append(node)

        elif context in [None, "", "None"]:
            servers_to_create_context.append(
                Server(
                    {
                        "ip": ip,
                        "username": username or current_user,
                    }
                )
            )

        else:
            updated_nodes.append(node)

    if servers_to_create_context:
        new_contexts = context_manager.create_servers_context(servers_to_create_context)
        updated_nodes.extend(new_contexts)

    return updated_nodes


def verify_populate_missing_values(settings: Settings, path: str) -> None:
    content: Dict[str, Any] = settings.get_content()
    current_user = getpass.getuser()

    context_manager = RemoteContextManager()

    mongodb = content.get("atomdb", {}).get("mongodb", {})

    if mongodb:
        mongodb_nodes = mongodb.get("nodes", [])

        if mongodb_nodes:
            mongodb["nodes"] = normalize_servers(mongodb_nodes, current_user, context_manager)

        if mongodb.get("cluster"):
            secret = mongodb.get("cluster_secret_key")

            if not secret or secret in ["None", ""]:
                mongodb["cluster_secret_key"] = get_rand_token(num_bytes=15)

    redis = content.get("atomdb", {}).get("redis", {})

    if redis:
        redis_nodes = redis.get("nodes", [])

        if redis_nodes:
            redis["nodes"] = normalize_servers(redis_nodes, current_user, context_manager)

    settings.set_content(content)

    context_manager.commit()

    settings.save()
