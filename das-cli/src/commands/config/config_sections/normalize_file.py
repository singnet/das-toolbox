import getpass
from copy import deepcopy
from typing import Any, Dict, List

from common.config.defaults import get_default_config_dict
from common.docker import RemoteContextManager
from common.docker.remote_context_manager import Server
from common.settings import Settings
from common.utils import get_rand_token

LOCAL_NODE_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0"}


def normalize_servers(
    nodes: List[Dict[str, Any]], current_user: str, context_manager: RemoteContextManager
) -> List[Dict[str, Any]]:
    # Every das-cli context was removed by _clear_existing_contexts, so any node that is
    # not on the default context needs a new one.
    updated_nodes = []

    for node in nodes:
        username = node.get("username")

        if node.get("context") == "default":
            if not username or username in ["root", "default"]:
                node["username"] = current_user

            updated_nodes.append(node)
            continue

        server = Server(
            {
                "ip": node.get("ip", "localhost"),
                "username": username or current_user,
            }
        )
        new_context = context_manager.create_servers_context([server])[0]
        updated_nodes.append({**node, **new_context})

    return updated_nodes


def _endpoint_host(endpoint: Any) -> str:
    if not isinstance(endpoint, str):
        return ""
    return endpoint.rsplit(":", 1)[0].strip()


def _default_peer_nodes(section: Dict[str, Any], current_user: str) -> List[Dict[str, Any]]:
    host = _endpoint_host(section.get("endpoint"))

    if not host or host in LOCAL_NODE_HOSTS:
        return [{"context": "default", "ip": "localhost", "username": current_user}]

    return [{"context": "", "ip": host, "username": current_user}]


def normalize_remote_peers(
    content: Dict[str, Any], current_user: str, context_manager: RemoteContextManager
) -> None:
    atomdb = content.get("atomdb", {})
    if atomdb.get("type") != "remotedb":
        return

    for peer in atomdb.get("remote_peers") or []:
        if not isinstance(peer, dict) or peer.get("type") != "redismongodb":
            continue

        for database in ("redis", "mongodb"):
            section = peer.get(database)
            if not isinstance(section, dict):
                continue

            nodes = section.get("nodes") or _default_peer_nodes(section, current_user)
            section["nodes"] = normalize_servers(nodes, current_user, context_manager)


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


def _validate_supplied_sections(current: Any, defaults: Dict[str, Any], path: str = "") -> None:
    if not isinstance(current, dict):
        raise ValueError(
            f"Invalid configuration entry '{path or 'root'}'. Expected an object. "
            "The file was left unchanged."
        )

    for key, default_value in defaults.items():
        if key in current and isinstance(default_value, dict):
            current_path = f"{path}.{key}" if path else key
            _validate_supplied_sections(current[key], default_value, current_path)


def _defaults_for_config(content: Dict[str, Any]) -> Dict[str, Any]:
    """Return canonical defaults trimmed to the active atomdb type (same rules as validation)."""
    expected = deepcopy(get_default_config_dict())
    _validate_supplied_sections(content, expected)
    if not expected:
        return {}

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
                content.get("atomdb", {}).get("adapterdb", {}).get("atomdb_backend", {}).get("type")
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

    normalize_remote_peers(content, current_user, context_manager)

    settings.set_content(content)

    context_manager.commit()

    settings.save()
