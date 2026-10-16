from unittest.mock import Mock

from services.container_services import ContainerServices
from shared.enums.action_types import ActionTypes


def remote_services(monkeypatch):
    config = Mock(user_profile={"profile_username": "levi"})
    config.load_raw_configuration.return_value = {"atomdb": {"type": "remotedb"}}
    monkeypatch.setattr(
        "services.container_services.AtomDbBuilder.build_remote_peer_configs",
        Mock(return_value={"192.0.2.1": {}, "192.0.2.2": {}}),
    )
    services = ContainerServices(config)
    services.build_das_cli_command = Mock(
        side_effect=lambda host, service_command, action: [host, service_command, action]
    )
    services.run_das_cli_command = Mock(return_value={"success": True})
    return services


def test_start_remote_atomdb_starts_peers_before_local_broker(monkeypatch):
    services = remote_services(monkeypatch)

    result = services.manage_container(ActionTypes.START, command="db", host="localhost")

    assert result["success"]
    assert [call.args[0] for call in services.run_das_cli_command.call_args_list] == [
        ["192.0.2.1", "db", "start"],
        ["192.0.2.2", "db", "start"],
        ["localhost", "atomdb-broker", "start"],
    ]


def test_stop_remote_atomdb_stops_local_broker_before_peers(monkeypatch):
    services = remote_services(monkeypatch)

    services.manage_container(ActionTypes.STOP, command="db", host="localhost")

    assert [call.args[0] for call in services.run_das_cli_command.call_args_list] == [
        ["localhost", "atomdb-broker", "stop"],
        ["192.0.2.2", "db", "stop"],
        ["192.0.2.1", "db", "stop"],
    ]


def test_selected_remote_host_only_starts_that_servers_databases(monkeypatch):
    services = remote_services(monkeypatch)

    services.manage_container(ActionTypes.START, command="db", host="192.0.2.1")

    services.run_das_cli_command.assert_called_once_with(["192.0.2.1", "db", "start"])
    services.web_config.load_raw_configuration.assert_not_called()