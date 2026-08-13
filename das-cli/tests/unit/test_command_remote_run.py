import json
import sys
import unittest
from unittest.mock import MagicMock, patch

from invoke.exceptions import UnexpectedExit

from common.command import Command
from common.service_response import CONTAINER_START_FAILURE_MESSAGE


class _RemoteProbeCommand(Command):
    name = "remote-probe"

    def run(self, **kwargs):
        return None


class RemoteRunTest(unittest.TestCase):
    def setUp(self):
        self.command = _RemoteProbeCommand()
        self.remote_kwargs = {"host": "example.test", "user": "tester"}

    def _mock_execution_context(self):
        context = MagicMock()
        context.command_path = "attention-broker start"
        context.to_str.return_value = "ctx"
        return context

    def _run_remote(self, result):
        with patch.object(self.command, "_get_remote_execution_context", return_value=self._mock_execution_context()):
            with patch.object(self.command, "_check_remote_config"):
                with patch("common.command.Connection") as connection_cls:
                    connection_cls.return_value.run.return_value = result
                    with patch("click.echo") as echo:
                        with patch.object(self.command, "stdout") as stdout:
                            with self.assertRaises(UnexpectedExit):
                                self.command._remote_run({}, self.remote_kwargs)
                            return echo, stdout

    def test_remote_service_failure_prints_streams_once_and_not_missing_cli(self):
        payload = {
            "service": "attention_broker",
            "action": "start",
            "status": "error",
            "message": CONTAINER_START_FAILURE_MESSAGE,
        }
        result = MagicMock()
        result.stdout = json.dumps(payload) + "\n"
        result.stderr = "Starting Attention Broker service...\n"
        result.failed = True
        result.exited = 1

        echo, stdout = self._run_remote(result)

        self.assertEqual(echo.call_count, 2)
        stdout.assert_not_called()
        combined = "".join(str(call.args[0]) for call in echo.call_args_list if call.args)
        self.assertEqual(combined.count(json.dumps(payload)), 1)
        self.assertEqual(combined.count("Starting Attention Broker service..."), 1)
        self.assertNotIn("missing on the remote machine", combined)

    def test_remote_missing_cli_reports_installation_error(self):
        result = MagicMock()
        result.stdout = ""
        result.stderr = "bash: line 1: das-cli: command not found\n"
        result.failed = True
        result.exited = 127

        echo, stdout = self._run_remote(result)

        self.assertEqual(echo.call_count, 1)
        stdout.assert_called_once()
        self.assertIn("missing on the remote machine", stdout.call_args.args[0])

    def test_remote_das_cli_missing_detects_exit_127(self):
        result = MagicMock()
        result.stdout = ""
        result.stderr = "something else"
        result.exited = 127

        self.assertTrue(Command._remote_das_cli_missing(result))

    def test_remote_das_cli_missing_rejects_structured_service_failure(self):
        result = MagicMock()
        result.stdout = json.dumps({"status": "error", "message": "failed"})
        result.stderr = ""
        result.exited = 1

        self.assertFalse(Command._remote_das_cli_missing(result))


if __name__ == "__main__":
    sys.path.insert(0, "src")
    unittest.main()
