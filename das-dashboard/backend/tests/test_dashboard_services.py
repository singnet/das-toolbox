import asyncio
from unittest.mock import Mock

from services.dashboard_services import DashboardServices


def test_initial_state_is_empty_before_first_configuration():
    config = Mock(config_dictionary={})

    result = asyncio.run(DashboardServices(config).fetch_initial_state())

    assert result == {"hosts": []}
    config.load_config_dictionary.assert_called_once_with(required=False)
    config.map_dashboard_hosts.assert_not_called()


def test_initial_state_lists_configured_hosts():
    config = Mock(config_dictionary={"db": {"host": "192.0.2.1"}})
    config.map_dashboard_hosts.return_value = [{"ip": "192.0.2.1"}]

    result = asyncio.run(DashboardServices(config).fetch_initial_state())

    assert result == {"hosts": [{"ip": "192.0.2.1"}]}