import asyncio
import sys
from pathlib import Path

import pytest

SRC_PATH = Path(__file__).resolve().parents[2] / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from commands.query.query_cli import QueryRun
from commands.query_agent.query_client import CommandRouterQueryClient


class _DummySettings:
    def get(self, key, default=None):
        return default


class _DummyConfigSettings:
    def __init__(self, content):
        self._content = content

    def get_content(self):
        return self._content

    def validate_configuration_file(self):
        return None


class _FakeStream:
    def __init__(self, messages):
        self._messages = list(messages)

    def __aiter__(self):
        self._iter = iter(self._messages)
        return self

    async def __anext__(self):
        try:
            return next(self._iter)
        except StopIteration as error:
            raise StopAsyncIteration from error


class _FakeConnection:
    def __init__(self, messages):
        self._stream = _FakeStream(messages)

    async def __aenter__(self):
        return self._stream

    async def __aexit__(self, exc_type, exc, tb):
        return False


class _HangingStream:
    def __aiter__(self):
        return self

    async def __anext__(self):
        await asyncio.Future()


class _HangingConnection:
    async def __aenter__(self):
        return _HangingStream()

    async def __aexit__(self, exc_type, exc, tb):
        return False


class _FakeQueryClient:
    def __init__(self):
        self.query_text = None
        self.parameters = None

    def create_execution(self, query_text, parameters=None):
        self.query_text = query_text
        self.parameters = parameters
        return {"execution_id": "exec-123"}

    async def stream_events(self, execution_id):
        assert execution_id == "exec-123"
        yield {"status": "completed"}


def _collect_events(client, execution_id):
    async def _collect():
        items = []
        async for event in client.stream_events(execution_id):
            items.append(event)
        return items

    return asyncio.run(_collect())


def test_stream_events_raises_on_clean_close_without_terminal_status(monkeypatch):
    client = CommandRouterQueryClient(settings=_DummySettings())

    first_endpoint_messages = [
        '{"command":"query_answers","params":{"execution_id":"exec-1","seq":1,"received_count":1,"answers":[{"x":1}]}}'
    ]

    def fake_connect(endpoint, open_timeout=10, close_timeout=5):
        del open_timeout, close_timeout
        if endpoint.endswith("/executions/ws/exec-1"):
            return _FakeConnection(first_endpoint_messages)
        return _FakeConnection([])

    monkeypatch.setattr(
        client,
        "_build_websocket_urls",
        lambda execution_id: [
            f"ws://localhost:40009/executions/ws/{execution_id}",
            f"ws://localhost:40009/command-router/ws/{execution_id}",
        ],
    )
    monkeypatch.setattr(client, "_load_websocket_client", lambda: (fake_connect, Exception))

    with pytest.raises(RuntimeError, match="stream closed before a terminal execution status"):
        _collect_events(client, "exec-1")


def test_stream_events_raises_on_inactivity_timeout(monkeypatch):
    client = CommandRouterQueryClient(settings=_DummySettings())
    client._stream_inactivity_timeout_seconds = 0.01

    def fake_connect(endpoint, open_timeout=10, close_timeout=5):
        del endpoint, open_timeout, close_timeout
        return _HangingConnection()

    monkeypatch.setattr(
        client,
        "_build_websocket_urls",
        lambda execution_id: [
            f"ws://localhost:40009/executions/ws/{execution_id}",
        ],
    )
    monkeypatch.setattr(client, "_load_websocket_client", lambda: (fake_connect, Exception))

    with pytest.raises(RuntimeError, match="inactivity timeout"):
        _collect_events(client, "exec-timeout")


def test_query_run_builds_execution_params_from_base_and_query_config():
    command = QueryRun(
        settings=_DummyConfigSettings(
            {
                "agents": {
                    "base_query": {
                        "params": {
                            "unique_assignment_flag": False,
                            "attention_update": 0,
                            "max_answers": 100,
                        }
                    },
                    "query": {
                        "params": {
                            "count_flag": True,
                            "max_answers": 7,
                        }
                    },
                }
            }
        ),
        command_router_query_client=None,
    )

    assert command._build_query_params_from_config() == {
        "unique_assignment_flag": False,
        "attention_update": 0,
        "max_answers": 7,
        "count_flag": True,
    }


def test_query_run_builds_execution_params_from_query_only_config():
    command = QueryRun(
        settings=_DummyConfigSettings(
            {
                "agents": {
                    "query": {
                        "params": {
                            "positive_importance_flag": True,
                            "unique_value_flag": True,
                            "count_flag": False,
                        }
                    }
                }
            }
        ),
        command_router_query_client=None,
    )

    assert command._build_query_params_from_config() == {
        "positive_importance_flag": True,
        "unique_value_flag": True,
        "count_flag": False,
    }


def test_query_run_builds_execution_params_from_base_only_config():
    command = QueryRun(
        settings=_DummyConfigSettings(
            {
                "agents": {
                    "base_query": {
                        "params": {
                            "unique_assignment_flag": True,
                            "attention_update": 3,
                            "attention_correlation": 1,
                            "attention_focus_strictness": 0.25,
                            "max_bundle_size": 250,
                            "max_answers": 5,
                            "use_link_template_cache": True,
                            "populate_metta_mapping": True,
                            "use_metta_as_query_tokens": True,
                            "allow_incomplete_chain_path": True,
                        }
                    }
                }
            }
        ),
        command_router_query_client=None,
    )

    assert command._build_query_params_from_config() == {
        "unique_assignment_flag": True,
        "attention_update": 3,
        "attention_correlation": 1,
        "attention_focus_strictness": 0.25,
        "max_bundle_size": 250,
        "max_answers": 5,
        "use_link_template_cache": True,
        "populate_metta_mapping": True,
        "use_metta_as_query_tokens": True,
        "allow_incomplete_chain_path": True,
    }


def test_query_run_builds_execution_params_with_full_supported_config_set():
    command = QueryRun(
        settings=_DummyConfigSettings(
            {
                "agents": {
                    "base_query": {
                        "params": {
                            "unique_assignment_flag": True,
                            "attention_update": 3,
                            "attention_correlation": 1,
                            "attention_focus_strictness": 0.75,
                            "max_bundle_size": 42,
                            "max_answers": 99,
                            "use_link_template_cache": True,
                            "populate_metta_mapping": True,
                            "use_metta_as_query_tokens": False,
                            "allow_incomplete_chain_path": True,
                        }
                    },
                    "query": {
                        "params": {
                            "positive_importance_flag": True,
                            "disregard_importance_flag": True,
                            "unique_value_flag": True,
                            "count_flag": True,
                        }
                    },
                }
            }
        ),
        command_router_query_client=None,
    )

    assert command._build_query_params_from_config() == {
        "unique_assignment_flag": True,
        "attention_update": 3,
        "attention_correlation": 1,
        "attention_focus_strictness": 0.75,
        "max_bundle_size": 42,
        "max_answers": 99,
        "use_link_template_cache": True,
        "populate_metta_mapping": True,
        "use_metta_as_query_tokens": False,
        "allow_incomplete_chain_path": True,
        "positive_importance_flag": True,
        "disregard_importance_flag": True,
        "unique_value_flag": True,
        "count_flag": True,
    }


def test_query_run_forwards_merged_config_params_to_execution_client(monkeypatch):
    fake_client = _FakeQueryClient()
    command = QueryRun(
        settings=_DummyConfigSettings(
            {
                "agents": {
                    "base_query": {
                        "params": {
                            "unique_assignment_flag": True,
                            "attention_update": 3,
                            "max_answers": 11,
                            "use_metta_as_query_tokens": True,
                        }
                    },
                    "query": {
                        "params": {
                            "positive_importance_flag": True,
                            "disregard_importance_flag": False,
                            "unique_value_flag": True,
                            "count_flag": True,
                            "max_answers": 2,
                        }
                    },
                }
            }
        ),
        command_router_query_client=fake_client,
    )

    monkeypatch.setattr(command, "log", lambda *args, **kwargs: None)
    monkeypatch.setattr(command, "stdout", lambda *args, **kwargs: None)

    command.run('LINK_TEMPLATE Expression 3 NODE Symbol Similarity NODE Symbol "human" VARIABLE S')

    assert fake_client.query_text == (
        'LINK_TEMPLATE Expression 3 NODE Symbol Similarity NODE Symbol "human" VARIABLE S'
    )
    assert fake_client.parameters == {
        "unique_assignment_flag": True,
        "attention_update": 3,
        "max_answers": 2,
        "use_metta_as_query_tokens": True,
        "positive_importance_flag": True,
        "disregard_importance_flag": False,
        "unique_value_flag": True,
        "count_flag": True,
    }


@pytest.mark.parametrize(
    "config",
    [
        {},
        {"agents": {}},
        {"agents": {"base_query": None, "query": {"params": None}}},
    ],
)
def test_query_run_ignores_missing_or_invalid_param_sections(config):
    command = QueryRun(
        settings=_DummyConfigSettings(config),
        command_router_query_client=None,
    )

    assert command._build_query_params_from_config() == {}


def test_query_run_omits_empty_values_from_execution_params():
    command = QueryRun(
        settings=_DummyConfigSettings(
            {
                "agents": {
                    "base_query": {
                        "params": {
                            "public_key_tokens": "",
                            "empty_spaces": "   ",
                            "none_value": None,
                            "empty_list": [],
                            "empty_dict": {},
                            "count_flag": False,
                            "attention_update": 0,
                            "max_answers": 3,
                        }
                    }
                }
            }
        ),
        command_router_query_client=None,
    )

    assert command._build_query_params_from_config() == {
        "count_flag": False,
        "attention_update": 0,
        "max_answers": 3,
    }


@pytest.fixture
def key_query_command():
    return QueryRun(
        settings=_DummyConfigSettings({"atomdb": {"uid": "local"}}),
        command_router_query_client=_FakeQueryClient(),
    )


@pytest.mark.parametrize("reference", ["absolute", "./key.pub", "keys/key.pub", "~/key.pub"])
def test_query_run_loads_key_from_explicit_path(
    key_query_command, tmp_path, monkeypatch, reference
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    key_path = tmp_path / ("keys/key.pub" if reference == "keys/key.pub" else "key.pub")
    key_path.parent.mkdir(parents=True, exist_ok=True)
    key_path.write_text("valid_key\n", encoding="utf-8")
    argument = str(key_path) if reference == "absolute" else reference

    assert key_query_command._load_public_key_tokens(argument) == "local valid_key"


def test_query_run_bare_name_falls_back_to_das_directory(key_query_command, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    (tmp_path / ".das").mkdir()
    (tmp_path / ".das/key.pub").write_text("valid_key", encoding="utf-8")

    assert key_query_command._load_public_key_tokens("key.pub") == "local valid_key"


def test_query_run_bare_name_prefers_current_directory(key_query_command, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    (tmp_path / ".das").mkdir()
    (tmp_path / ".das/key.pub").write_text("valid_key", encoding="utf-8")
    (tmp_path / "key.pub").write_text("unknown_key", encoding="utf-8")

    assert key_query_command._load_public_key_tokens("key.pub") == "local unknown_key"


@pytest.mark.parametrize("reference", ["absolute", "./key.pub", "keys/key.pub", "~/key.pub"])
def test_query_run_explicit_missing_path_never_falls_back(
    key_query_command, tmp_path, monkeypatch, reference
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    (tmp_path / ".das").mkdir()
    (tmp_path / ".das/key.pub").write_text("valid_key", encoding="utf-8")
    argument = str(tmp_path / "key.pub") if reference == "absolute" else reference

    with pytest.raises(FileNotFoundError, match="Public key file not found"):
        key_query_command._load_public_key_tokens(argument)


@pytest.mark.parametrize("content", ["", " \n", "two tokens", "key\nsecond_key"])
def test_query_run_invalid_file_never_falls_back(key_query_command, tmp_path, monkeypatch, content):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    (tmp_path / ".das").mkdir()
    (tmp_path / ".das/key.pub").write_text("valid_key", encoding="utf-8")
    (tmp_path / "key.pub").write_text(content, encoding="utf-8")

    with pytest.raises(ValueError, match="single non-empty token"):
        key_query_command._load_public_key_tokens("key.pub")


def test_query_run_missing_key_fails_before_http(key_query_command, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))

    with pytest.raises(FileNotFoundError, match="Public key file not found"):
        key_query_command.run("query", public_key="missing.pub")

    assert key_query_command._command_router_query_client.query_text is None


@pytest.mark.parametrize(
    "failure, expected_error",
    [
        ("directory", IsADirectoryError),
        ("encoding", UnicodeDecodeError),
        ("unreadable", PermissionError),
    ],
)
def test_query_run_unreadable_key_never_falls_back_or_calls_http(
    key_query_command, tmp_path, monkeypatch, failure, expected_error
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    (tmp_path / ".das").mkdir()
    (tmp_path / ".das/key.pub").write_text("valid_key", encoding="utf-8")
    key_path = tmp_path / "key.pub"
    if failure == "directory":
        key_path.mkdir()
    elif failure == "encoding":
        key_path.write_bytes(b"\xff")
    else:
        key_path.write_text("valid_key", encoding="utf-8")
        original_read = Path.read_text

        def deny_key_read(path, *args, **kwargs):
            if path.name == "key.pub" and path.parent == Path("."):
                raise PermissionError("Public key file is not readable")
            return original_read(path, *args, **kwargs)

        monkeypatch.setattr(Path, "read_text", deny_key_read)

    with pytest.raises(expected_error):
        key_query_command.run("query", public_key="key.pub")
    assert key_query_command._command_router_query_client.query_text is None


@pytest.mark.parametrize("uid", [None, "", "two uids", "\n", 42])
def test_query_run_rejects_invalid_uid_before_http(key_query_command, tmp_path, uid):
    key_path = tmp_path / "key.pub"
    key_path.write_text("valid_key", encoding="utf-8")
    key_query_command._settings = _DummyConfigSettings({"atomdb": {"uid": uid}})

    with pytest.raises(ValueError, match="atomdb.uid"):
        key_query_command.run("query", public_key=str(key_path))
    assert key_query_command._command_router_query_client.query_text is None


@pytest.mark.parametrize("reference", ["", "   "])
def test_query_run_rejects_empty_key_option_before_http(key_query_command, reference):
    with pytest.raises(ValueError, match="Public key file name must not be empty"):
        key_query_command.run("query", public_key=reference)
    assert key_query_command._command_router_query_client.query_text is None


def test_query_run_forwards_file_key_and_ignores_config_keys(tmp_path, monkeypatch):
    key_path = tmp_path / "key.pub"
    key_path.write_text("file_key", encoding="utf-8")
    fake_client = _FakeQueryClient()
    command = QueryRun(
        settings=_DummyConfigSettings(
            {
                "atomdb": {"uid": "custom_uid", "public_keys": ["config_key"]},
                "agents": {
                    "base_query": {"params": {"public_key_tokens": "local base_key"}},
                    "query": {
                        "params": {"public_key_tokens": "local query_key", "count_flag": True}
                    },
                },
            }
        ),
        command_router_query_client=fake_client,
    )
    monkeypatch.setattr(command, "log", lambda *args, **kwargs: None)
    monkeypatch.setattr(command, "stdout", lambda *args, **kwargs: None)

    command.run("query", public_key=str(key_path))
    assert fake_client.parameters == {
        "count_flag": True,
        "public_key_tokens": "custom_uid file_key",
    }

    command.run("query")
    assert fake_client.parameters == {"count_flag": True}
    assert command._settings.get_content()["atomdb"]["public_keys"] == ["config_key"]


def test_query_client_builds_execution_payload_with_command_and_params_contract():
    client = CommandRouterQueryClient(settings=_DummySettings())
    query_text = 'LINK_TEMPLATE Expression 3 NODE Symbol Similarity NODE Symbol "human" VARIABLE S'

    payload = client._build_query_execution_payload(
        query_text=query_text,
        parameters={
            "count_flag": True,
            "max_answers": 5,
        },
    )

    assert payload["command"] == "query"
    assert payload["params"]["query"] == {
        "syntax": "metta",
        "tokens": [query_text],
    }
    assert payload["params"]["count_flag"] is True
    assert payload["params"]["max_answers"] == 5
    assert "command_type" not in payload
    assert "command_text" not in payload
    assert "command_params" not in payload


def test_query_client_rejects_query_param_override_in_execution_payload():
    client = CommandRouterQueryClient(settings=_DummySettings())

    with pytest.raises(ValueError, match="Reserved parameter 'query' cannot be overridden"):
        client._build_query_execution_payload(
            query_text='LINK_TEMPLATE Expression 3 NODE Symbol Similarity NODE Symbol "human" VARIABLE S',
            parameters={"query": {"syntax": "metta", "tokens": ["override"]}},
        )
