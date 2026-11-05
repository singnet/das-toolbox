import sys
from pathlib import Path

SRC_PATH = Path(__file__).resolve().parents[2] / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from common.command import Command  # noqa: E402


class _Result:
    failed = False
    stdout = "log line\n"
    stderr = ""


class _Context:
    command_path = "logs das"

    def to_str(self, include_ssh=False):
        return "encoded-context"


def _command(monkeypatch):
    calls = []

    class _Connection:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def run(self, command, hide=True, warn=False):
            calls.append({"command": command, "hide": hide, "stdout": _Result.stdout})
            return _Result()

    monkeypatch.setattr("common.command.Connection", _Connection)
    command = Command()
    command._get_remote_execution_context = lambda: _Context()
    command._check_remote_config = lambda remote_kwargs: None
    return command, calls


def test_remote_follow_streams_output_while_the_command_is_running(monkeypatch):
    command, calls = _command(monkeypatch)

    command._remote_run({"follow": True}, {"host": "peer.example"})

    assert calls[-1]["hide"] is False
    assert "--follow" in calls[-1]["command"]
    assert calls[-1]["stdout"] == "log line\n"


def test_remote_command_without_follow_hides_output_until_exit(monkeypatch):
    command, calls = _command(monkeypatch)

    command._remote_run({"follow": False}, {"host": "peer.example"})

    assert calls[-1]["hide"] is True
    assert "--follow" not in calls[-1]["command"]
