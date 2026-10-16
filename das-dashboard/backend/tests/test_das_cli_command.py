import shlex
from unittest.mock import Mock

from shared.utils.das_cli_command import build_host_cli_command


def test_local_command_does_not_use_ssh():
    config = Mock()

    command = build_host_cli_command(config, "localhost", ["system", "status", "-o", "json"])

    assert command == ["das-cli", "system", "status", "-o", "json"]


def test_remote_command_uses_ssh_and_the_servers_own_configuration():
    config = Mock(user_profile={"profile_username": "levi", "profile_ssh_keypath": "/key.pem"})

    command = build_host_cli_command(config, "192.0.2.1", ["db", "start", "-o", "json"])

    assert command[0] == "ssh"
    assert command[command.index("-i") + 1] == "/key.pem"
    assert command[command.index("-l") + 1] == "levi"
    assert command[-2] == "192.0.2.1"
    assert shlex.split(command[-1]) == ["das-cli", "db", "start", "-o", "json"]
    assert "--remote" not in command[-1]
    assert "BatchMode=yes" in command
    assert "IdentitiesOnly=yes" in command


def test_remote_file_path_is_passed_as_a_literal_argument():
    config = Mock(user_profile={})
    path = "/tmp/my file';$(touch /tmp/unwanted).metta"

    command = build_host_cli_command(config, "192.0.2.1", ["metta", "load", path])

    assert shlex.split(command[-1]) == ["das-cli", "metta", "load", path]