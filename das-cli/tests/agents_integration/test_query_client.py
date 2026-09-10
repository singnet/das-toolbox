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

    monkeypatch.setattr(client, "_build_websocket_urls", lambda execution_id: [
        f"ws://localhost:40009/executions/ws/{execution_id}",
        f"ws://localhost:40009/command-router/ws/{execution_id}",
    ])
    monkeypatch.setattr(client, "_load_websocket_client", lambda: (fake_connect, Exception))

    with pytest.raises(RuntimeError, match="stream closed before a terminal execution status"):
        _collect_events(client, "exec-1")


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
