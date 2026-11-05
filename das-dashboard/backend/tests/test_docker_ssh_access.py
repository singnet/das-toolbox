import pytest

from shared.exceptions.custom_exceptions import CustomValueError
from shared.utils.docker_ssh_access import ensure_docker_ssh_access


def test_invalid_peer_host_is_rejected_before_ssh_setup(monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError("SSH setup should not start for an invalid host")

    monkeypatch.setattr("shared.utils.docker_ssh_access.RemoteScpService", fail)

    with pytest.raises(CustomValueError, match="Invalid peer host"):
        ensure_docker_ssh_access(object(), ["db.example", "bad host\n  ProxyCommand touch /tmp/pwned"])


@pytest.mark.parametrize("host", ["db.example", "localhost", "10.0.0.8", "2001:db8::1"])
def test_valid_peer_hosts_are_accepted(monkeypatch, host):
    class _Scp:
        def __init__(self, web_config):
            self.web_config = web_config

        def ensure_profile(self):
            return "das", "/tmp/das-key"

    monkeypatch.setattr("shared.utils.docker_ssh_access.RemoteScpService", _Scp)
    monkeypatch.setattr("shared.utils.docker_ssh_access._write_ssh_config", lambda *args: None)
    monkeypatch.setattr("shared.utils.docker_ssh_access._add_known_hosts", lambda *args: None)

    ensure_docker_ssh_access(object(), [host])
