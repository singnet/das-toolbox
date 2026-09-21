import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from common.config import defaults


def _set_default_path(monkeypatch: pytest.MonkeyPatch, path) -> None:
    monkeypatch.setattr(defaults, "DEFAULT_CONFIGFILE_PATH", str(path))


def test_get_default_config_dict_loads_valid_object(tmp_path, monkeypatch):
    config_path = tmp_path / "default.json"
    config_path.write_text(json.dumps({"schema_version": 1, "atomdb": {}}), encoding="utf-8")

    _set_default_path(monkeypatch, config_path)
    result = defaults.get_default_config_dict()

    assert result["schema_version"] == 1
    assert isinstance(result, dict)


def test_get_default_config_dict_raises_for_missing_file(tmp_path, monkeypatch):
    config_path = tmp_path / "missing-default.json"
    _set_default_path(monkeypatch, config_path)

    with pytest.raises(FileNotFoundError, match="Default config file not found"):
        defaults.get_default_config_dict()


def test_get_default_config_dict_raises_for_non_object_root(tmp_path, monkeypatch):
    config_path = tmp_path / "default-list.json"
    config_path.write_text(json.dumps(["not", "an", "object"]), encoding="utf-8")

    _set_default_path(monkeypatch, config_path)

    with pytest.raises(ValueError, match="Default config root must be a JSON object"):
        defaults.get_default_config_dict()


def test_get_default_config_dict_normalizes_node_usernames(tmp_path, monkeypatch):
    config_path = tmp_path / "default-with-nodes.json"
    config = {
        "schema_version": 1,
        "atomdb": {
            "redis": {
                "nodes": [
                    {"context": "default", "ip": "10.0.0.10", "username": "explicit-default"},
                    {"context": "ssh-context", "ip": "localhost", "username": "explicit-local"},
                    {"context": "ssh-context", "ip": "10.0.0.11", "username": "explicit-remote"},
                ]
            },
            "mongodb": {
                "nodes": [
                    {"context": "ssh-context", "ip": "127.0.0.1", "username": "mongo-local"},
                    {"context": "ssh-context", "ip": "10.0.0.12", "username": "mongo-remote"},
                ]
            },
            "adapterdb": {
                "atomdb_backend": {
                    "mongodb": {
                        "nodes": [
                            {"context": "ssh-context", "ip": "::1", "username": "backend-local"},
                            {
                                "context": "ssh-context",
                                "ip": "10.0.0.13",
                                "username": "backend-remote",
                            },
                        ]
                    }
                }
            },
        },
    }
    config_path.write_text(json.dumps(config), encoding="utf-8")

    _set_default_path(monkeypatch, config_path)
    monkeypatch.setattr(defaults.getpass, "getuser", lambda: "normalized-user")

    result = defaults.get_default_config_dict()

    redis_nodes = result["atomdb"]["redis"]["nodes"]
    assert redis_nodes[0]["username"] == "normalized-user"
    assert redis_nodes[1]["username"] == "normalized-user"
    assert redis_nodes[2]["username"] == "explicit-remote"

    mongodb_nodes = result["atomdb"]["mongodb"]["nodes"]
    assert mongodb_nodes[0]["username"] == "normalized-user"
    assert mongodb_nodes[1]["username"] == "mongo-remote"

    backend_nodes = result["atomdb"]["adapterdb"]["atomdb_backend"]["mongodb"]["nodes"]
    assert backend_nodes[0]["username"] == "normalized-user"
    assert backend_nodes[1]["username"] == "backend-remote"
