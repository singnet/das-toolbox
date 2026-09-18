import json
import getpass
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict

from settings.config import DEFAULT_CONFIGFILE_PATH


def _is_local_ip(ip: Any) -> bool:
    if not isinstance(ip, str):
        return False
    return ip in {"localhost", "127.0.0.1", "::1"}


def _normalize_dynamic_usernames(content: Dict[str, Any], current_user: str) -> Dict[str, Any]:
    def normalize_nodes(nodes: Any) -> None:
        if not isinstance(nodes, list):
            return

        for node in nodes:
            if not isinstance(node, dict):
                continue

            context = node.get("context")
            ip = node.get("ip")

            if context == "default" or _is_local_ip(ip):
                node["username"] = current_user

    atomdb = content.get("atomdb")
    if not isinstance(atomdb, dict):
        return content

    redis = atomdb.get("redis")
    if isinstance(redis, dict):
        normalize_nodes(redis.get("nodes"))

    mongodb = atomdb.get("mongodb")
    if isinstance(mongodb, dict):
        normalize_nodes(mongodb.get("nodes"))

    adapterdb = atomdb.get("adapterdb")
    if isinstance(adapterdb, dict):
        atomdb_backend = adapterdb.get("atomdb_backend")
        if isinstance(atomdb_backend, dict):
            backend_mongodb = atomdb_backend.get("mongodb")
            if isinstance(backend_mongodb, dict):
                normalize_nodes(backend_mongodb.get("nodes"))

    return content


def get_default_config_dict() -> Dict[str, Any]:
    default_path = Path(DEFAULT_CONFIGFILE_PATH).expanduser().resolve(strict=False)

    if not default_path.exists():
        raise FileNotFoundError(f"Default config file not found: {default_path}")

    with open(default_path, "r", encoding="utf-8") as config_file:
        content = json.load(config_file)

    if not isinstance(content, dict):
        raise ValueError(f"Default config root must be a JSON object: {default_path}")

    return _normalize_dynamic_usernames(content, getpass.getuser())


def get_default_config_schema_dict() -> Dict[str, Any]:
    def to_schema(value: Any) -> Any:
        if isinstance(value, dict):
            return {key: to_schema(item) for key, item in value.items()}
        return None

    defaults = get_default_config_dict()
    return deepcopy(to_schema(defaults))
