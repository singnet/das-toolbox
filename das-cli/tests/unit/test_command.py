import unittest
from unittest.mock import Mock, patch

from common.command import Command


class RemoteCommandOutputTest(unittest.TestCase):
    def setUp(self):
        self.command = Command()
        self.command._output_format = "json"
        context = Mock(command_path="system status")
        context.to_str.return_value = "test-context"
        self.command._get_remote_execution_context = Mock(return_value=context)
        self.command._check_remote_config = Mock()
        self.command._echo_remote_streams = Mock()
        self.result = Mock(failed=False)

    def run_remote(self, kwargs):
        with patch("common.command.Connection") as connection:
            connection.return_value.run.return_value = self.result
            self.command._remote_run(kwargs, {"host": "test-host"})
            return connection.return_value.run.call_args

    def test_stream_argument_forwards_output_live(self):
        args, kwargs = self.run_remote({"stream": True})

        self.assertIn("--stream", args[0])
        self.assertFalse(kwargs["hide"])
        self.command._echo_remote_streams.assert_not_called()

    def test_stream_attribute_forwards_output_live(self):
        self.command._stream = True

        args, kwargs = self.run_remote({})

        self.assertIn("--stream", args[0])
        self.assertFalse(kwargs["hide"])
        self.command._echo_remote_streams.assert_not_called()

    def test_non_stream_output_is_echoed_once(self):
        args, kwargs = self.run_remote({"stream": False})

        self.assertNotIn("--stream", args[0])
        self.assertTrue(kwargs["hide"])
        self.command._echo_remote_streams.assert_called_once_with(self.result)