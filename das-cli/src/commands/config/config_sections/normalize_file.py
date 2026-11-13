import getpass
from copy import deepcopy
from typing import Any, Dict, List, Set

from common.config.defaults import get_default_config_dict
from common.docker import RemoteContextManager
from common.docker.remote_context_manager import Server
from common.settings import Settings
from common.utils import get_rand_token

LOCAL_NODE_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0"}


def _invalid_entry(path: str, expected: str) -> ValueError:
    return ValueError(
        f"Invalid configuration entry '{path}'. Expected {expected}. "
        "The file was left unchanged."
    )


def _validate_node_list(nodes: Any, path: str) -> None:
    if not isinstance(nodes, list):
        raise _invalid_entry(path, "a list of node objects")

    for index, node in enumerate(nodes):
        if not isinstance(node, dict):
            raise _invalid_entry(f"{path}[{index}]", "a node object")


def _validate_database_nodes(section: Any, path: str) -> None:
    if section is None:
        return

    if not isinstance(section, dict):
        raise _invalid_entry(path, "an object")

    if "nodes" in section and section["nodes"] is not None:
        _validate_node_list(section["nodes"], f"{path}.nodes")


def _validate_nodes_for_context_setup(content: Dict[str, Any]) -> None:
    """Reject malformed nodes before das-cli Docker contexts are removed."""
    atomdb = content.get("atomdb")
    if not isinstance(atomdb, dict):
        return

    for database in ("redis", "mongodb"):
        if database in atomdb:
            _validate_database_nodes(atomdb.get(database), f"atomdb.{database}")

    if atomdb.get("type") != "remotedb":
        return

    peers = atomdb.get("remote_peers")
    if peers is None:
        return

    if not isinstance(peers, list):
        raise _invalid_entry("atomdb.remote_peers", "a list of peer objects")

    for index, peer in enumerate(peers):
        peer_path = f"atomdb.remote_peers[{index}]"
        if not isinstance(peer, dict):
            raise _invalid_entry(peer_path, "a peer object")

        for database in ("redis", "mongodb"):
            if database in peer:
                _validate_database_nodes(peer.get(database), f"{peer_path}.{database}")


def normalize_servers(
    nodes: List[Dict[str, Any]],
    current_user: str,
    context_manager: RemoteContextManager,
    removed_contexts: Set[str],
) -> List[Dict[str, Any]]:
    # Recreate contexts that cleanup removed, and nodes that have none.
    # A supplied context that was not removed keeps its connection settings.
    updated_nodes = []

    for node in nodes:
        if not isinstance(node, dict):
            raise _invalid_entry("nodes", "a node object")

        username = node.get("username")
        context = node.get("context")

        if context == "default":
            if not username or username in ["root", "default"]:
                node["username"] = current_user

            updated_nodes.append(node)
            continue

        if context and context not in removed_contexts:
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


def assemble_db_start_targets(content: Dict[str, Any], current_user: str) -> None:
    """Builds db_start_targets from each RemoteDB peer's local persistence.
    This is necessary for das-cli and the dashboard to operate.

    In-memory persistence is skipped.
    """
    atomdb = content.get("atomdb") or {}
    if not isinstance(atomdb, dict) or atomdb.get("type") != "remotedb":
        content.pop("db_start_targets", None)
        return

    previous = {
        item.get("codename"): item
        for item in content.get("db_start_targets") or []
        if isinstance(item, dict) and item.get("codename")
    }
    targets = []
    for peer in atomdb.get("remote_peers") or []:
        if not isinstance(peer, dict):
            continue
        _strip_database_nodes(peer)
        local_persistence = peer.get("local_persistence") or {}
        if not isinstance(local_persistence, dict):
            continue
        _strip_database_nodes(local_persistence)

        persistence_type = local_persistence.get("type")
        if persistence_type not in {"redismongodb", "morkdb"}:
            continue

        host = _persistence_host(local_persistence, persistence_type)
        local = not host or host in LOCAL_NODE_HOSTS
        derived_ip = "localhost" if local else host
        codename = local_persistence.get("context") or f"{peer.get('uid') or 'peer'}-local"
        saved = previous.get(codename) or {}
        nodes = _saved_nodes(saved, derived_ip, current_user, local)
        targets.append(
            {
                "codename": codename,
                "type": persistence_type,
                "nodes": nodes,
            }
        )

    content["db_start_targets"] = targets


def _saved_nodes(saved: Dict[str, Any], derived_ip: str, current_user: str, local: bool) -> list:
    nodes = saved.get("nodes")
    if isinstance(nodes, list) and nodes:
        return [dict(node) for node in nodes if isinstance(node, dict)]

    if saved.get("ip") or saved.get("username") or saved.get("context"):
        return [
            {
                "context": saved.get("context") or ("default" if local else ""),
                "ip": saved.get("ip") or derived_ip,
                "username": saved.get("username") or current_user,
            }
        ]

    return [
        {
            "context": "default" if local else "",
            "ip": derived_ip,
            "username": current_user,
        }
    ]


def _strip_database_nodes(section: Dict[str, Any]) -> None:
    for database in ("redis", "mongodb", "morkdb"):
        database_section = section.get(database)
        if isinstance(database_section, dict):
            database_section.pop("nodes", None)


def _persistence_host(local_persistence: Dict[str, Any], persistence_type: str) -> str:
    if persistence_type == "redismongodb":
        endpoint = (local_persistence.get("redis") or {}).get("endpoint")
        if not endpoint:
            endpoint = (local_persistence.get("mongodb") or {}).get("endpoint")
    else:
        endpoint = (local_persistence.get("morkdb") or {}).get("endpoint")
        if not endpoint:
            endpoint = (local_persistence.get("mongodb") or {}).get("endpoint")
    return _endpoint_host(endpoint)


def normalize_db_start_targets(
    content: Dict[str, Any],
    current_user: str,
    context_manager: RemoteContextManager,
    removed_contexts: Set[str],
) -> None:
    targets = content.get("db_start_targets")
    if not isinstance(targets, list):
        return

    for target in targets:
        if not isinstance(target, dict) or target.get("type") not in {"redismongodb", "morkdb"}:
            continue

        nodes = target.get("nodes")
        if not isinstance(nodes, list) or not nodes:
            nodes = [
                {
                    "context": target.get("context") or "",
                    "ip": target.get("ip") or "localhost",
                    "username": target.get("username") or current_user,
                }
            ]
        target["nodes"] = normalize_servers(nodes, current_user, context_manager, removed_contexts)
        target.pop("context", None)
        target.pop("ip", None)
        target.pop("username", None)


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

    _validate_nodes_for_context_setup(content)

    current_user = getpass.getuser()

    context_manager = RemoteContextManager()
    assemble_db_start_targets(content, current_user)
    removed_contexts = set(context_manager._clear_existing_contexts())

    mongodb = content.get("atomdb", {}).get("mongodb", {})

    if mongodb:
        mongodb_nodes = mongodb.get("nodes", [])

        if mongodb_nodes:
            mongodb["nodes"] = normalize_servers(
                mongodb_nodes, current_user, context_manager, removed_contexts
            )

        if mongodb.get("cluster"):
            secret = mongodb.get("cluster_secret_key")

            if not secret or secret in ["None", ""]:
                mongodb["cluster_secret_key"] = get_rand_token(num_bytes=15)

    redis = content.get("atomdb", {}).get("redis", {})

    if redis:
        redis_nodes = redis.get("nodes", [])

        if redis_nodes:
            redis["nodes"] = normalize_servers(
                redis_nodes, current_user, context_manager, removed_contexts
            )

    normalize_db_start_targets(content, current_user, context_manager, removed_contexts)

    settings.set_content(content)

    context_manager.commit()

    settings.save()
