import sys
from pathlib import Path

import pytest

SRC_PATH = Path(__file__).resolve().parents[2] / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from commands.config.config_sections.normalize_file import (  # noqa: E402
    normalize_servers,
    verify_populate_missing_values,
)


class _ContextManager:
    def __init__(self):
        self.created = []

    def create_servers_context(self, servers):
        self.created.append(servers)
        server = servers[0]
        return [{"context": "generated", "ip": server["ip"], "username": server["username"]}]


def test_supplied_context_is_kept_when_cleanup_did_not_remove_it():
    manager = _ContextManager()
    node = {"context": "prod", "ip": "10.0.0.8", "username": "alice", "port": 22}

    result = normalize_servers([node], "bob", manager, removed_contexts=set())

    assert result == [node]
    assert manager.created == []


def test_removed_das_cli_context_is_recreated():
    manager = _ContextManager()
    node = {"context": "old-uuid", "ip": "10.0.0.8", "username": "alice"}

    result = normalize_servers([node], "bob", manager, removed_contexts={"old-uuid"})

    assert result[0]["context"] == "generated"
    assert result[0]["ip"] == "10.0.0.8"
    assert result[0]["username"] == "alice"
    assert manager.created == [[{"ip": "10.0.0.8", "username": "alice"}]]


def test_missing_context_is_created():
    manager = _ContextManager()

    result = normalize_servers(
        [{"context": "", "ip": "10.0.0.9", "username": "alice"}],
        "bob",
        manager,
        removed_contexts=set(),
    )

    assert result[0]["context"] == "generated"
    assert manager.created


def test_invalid_nodes_do_not_remove_docker_contexts(monkeypatch):
    monkeypatch.setattr(
        "commands.config.config_sections.normalize_file.get_default_config_dict",
        lambda: {"atomdb": {"type": "redismongodb", "redis": {"nodes": []}, "mongodb": {}}},
    )
    cleared = []

    class _Manager:
        def _clear_existing_contexts(self):
            cleared.append(True)
            return []

        def commit(self):
            raise AssertionError("context changes should not be committed")

    monkeypatch.setattr(
        "commands.config.config_sections.normalize_file.RemoteContextManager",
        _Manager,
    )

    class _Settings:
        def get_content(self):
            return {
                "atomdb": {
                    "type": "redismongodb",
                    "redis": {"nodes": [None]},
                    "mongodb": {},
                }
            }

        def set_content(self, content):
            raise AssertionError("rejected configuration should not be saved")

        def save(self):
            raise AssertionError("rejected configuration should not be saved")

    with pytest.raises(ValueError, match=r"atomdb\.redis\.nodes\[0\]"):
        verify_populate_missing_values(_Settings(), "/tmp/das-config.json")

    assert cleared == []
