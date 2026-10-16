import asyncio
from unittest.mock import Mock

from services.config_services import ConfigServices


def test_remote_db_save_provisions_server_specific_configuration(monkeypatch):
    service = object.__new__(ConfigServices)
    service.web_config = Mock()
    service.web_config.user_profile = {"profile_username": "levi"}
    service._scp_config_sync = Mock(return_value="/home/levi/.das/config.json")
    peer_config = {"atomdb": {"type": "redismongodb", "uid": "peer-one"}}
    project = Mock(return_value={"192.0.2.1": peer_config})
    monkeypatch.setattr(
        "services.config_services.AtomDbBuilder.build_remote_peer_configs", project
    )
    select_config = Mock()
    monkeypatch.setattr("services.config_services.set_das_cli_config", select_config)

    hosts = asyncio.run(
        service._propagate_config_to_remotes(
            {"atomdb": {"type": "remotedb", "remote_peers": [{"uid": "peer-one"}]}}
        )
    )

    assert hosts == ["192.0.2.1"]
    service.web_config.map_remote_hosts.assert_not_called()
    service._scp_config_sync.assert_called_once_with("192.0.2.1", peer_config)
    select_config.assert_called_once_with(
        "/home/levi/.das/config.json", web_config=service.web_config, host="192.0.2.1"
    )


def test_non_remote_db_save_keeps_existing_propagation(monkeypatch):
    service = object.__new__(ConfigServices)
    service.web_config = Mock()
    service.web_config.map_remote_hosts.return_value = [{"ip": "192.0.2.1"}]
    service._scp_config_sync = Mock(return_value="/home/levi/.das/config.json")
    select_config = Mock()
    monkeypatch.setattr("services.config_services.set_das_cli_config", select_config)
    config = {"atomdb": {"type": "redismongodb"}}

    hosts = asyncio.run(service._propagate_config_to_remotes(config))

    assert hosts == ["192.0.2.1"]
    service._scp_config_sync.assert_called_once_with("192.0.2.1", config)
    select_config.assert_called_once_with(
        "/home/levi/.das/config.json", web_config=service.web_config, host="192.0.2.1"
    )