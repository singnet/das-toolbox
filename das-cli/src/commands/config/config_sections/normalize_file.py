import getpass
from copy import deepcopy
from typing import Any, Dict, List

from common.config.core import get_core_defaults_dict
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


def _fill_missing_values(current: Any, defaults: Any) -> Any:
    """Add keys present in defaults but missing in current; never overwrite user values."""
    if not isinstance(defaults, dict):
        return current if current is not None else deepcopy(defaults)

    result = dict(current) if isinstance(current, dict) else {}
    for key, default_value in defaults.items():
        if key not in result:
            result[key] = deepcopy(default_value)
        else:
            result[key] = _fill_missing_values(result[key], default_value)
    return result


def _defaults_for_config(content: Dict[str, Any]) -> Dict[str, Any]:
    """Return schema defaults trimmed to the active atomdb type (same rules as validation)."""
    expected = deepcopy(get_core_defaults_dict())
    default_atomdb_type = expected.get("atomdb", {}).get("type", "redismongodb")
    atomdb_type = content.get("atomdb", {}).get("type") or default_atomdb_type
    atomdb_section = expected["atomdb"]

    if atomdb_type != "adapterdb":
        atomdb_section.pop("adapterdb", None)

    if atomdb_type != "remotedb":
        atomdb_section.pop("remote_peers", None)

    if atomdb_type != "morkdb":
        atomdb_section.pop("mongodb", None)
        atomdb_section.pop("morkdb", None)

    if atomdb_type != "redismongodb":
        atomdb_section.pop("mongodb", None)
        atomdb_section.pop("redis", None)

    adapterdb = atomdb_section.get("adapterdb")
    if adapterdb:
        backend = adapterdb.get("atomdb_backend")
        if backend:
            backend_type = (
                content.get("atomdb", {})
                .get("adapterdb", {})
                .get("atomdb_backend", {})
                .get("type")
            ) or backend.get("type")

            if backend_type != "redismongodb":
                backend.pop("redis", None)
                backend.pop("mongodb", None)

            if backend_type != "morkdb":
                backend.pop("morkdb", None)

            if backend_type != "inmemorydb":
                backend.pop("inmemorydb", None)

    return expected


def verify_populate_missing_values(settings: Settings, path: str) -> None:
    content: Dict[str, Any] = settings.get_content()
    content = _fill_missing_values(content, _defaults_for_config(content))

    base_query_params = content.get("agents", {}).get("base_query", {}).get("params")
    if isinstance(base_query_params, dict) and "attention_focus_strictness" in base_query_params:
        base_query_params["attention_focus_strictness"] = float(
            base_query_params["attention_focus_strictness"]
        )

    current_user = getpass.getuser()

    context_manager = RemoteContextManager()
    context_manager._clear_existing_contexts()

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
