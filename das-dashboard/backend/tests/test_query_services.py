import pytest

from services.query_services import QueryServices
from shared.exceptions.custom_exceptions import CustomValueError


class _WebConfig:
    def __init__(self, uid: str = "local", atomdb_type: str = "redismongodb", remote_peers=None):
        self.atomdb = {"uid": uid, "type": atomdb_type}
        if remote_peers is not None:
            self.atomdb["remote_peers"] = remote_peers

    def load_raw_configuration(self):
        return {"atomdb": self.atomdb}


def _service(
    uid: str = "local",
    atomdb_type: str = "redismongodb",
    remote_peers=None,
) -> QueryServices:
    return QueryServices(_WebConfig(uid, atomdb_type, remote_peers))


def _capture_payload(service: QueryServices, monkeypatch, public_key: str | None) -> dict:
    captured = {}

    def capture_request(method, path, **kwargs):
        captured["method"] = method
        captured["path"] = path
        captured["payload"] = kwargs["json"]
        return object()

    monkeypatch.setattr(service, "_call_http_proxy", capture_request)
    service.create_query_execution(
        '(Similarity "human" %C)',
        {"count_flag": True, "public_key_tokens": "legacy config key"},
        public_key,
    )
    return captured


def test_uploaded_key_overrides_config_key_tokens(monkeypatch):
    service = _service(uid="dashboard-user")
    captured = _capture_payload(service, monkeypatch, "query_key\n")

    assert captured["payload"]["params"]["public_key_tokens"] == "dashboard-user query_key"
    assert captured["payload"]["params"]["count_flag"] is True
    assert captured["payload"]["params"]["query"]["tokens"] == ['(Similarity "human" %C)']


def test_uploaded_key_is_reused_for_every_remote_peer(monkeypatch):
    service = _service(
        uid="federation",
        atomdb_type="remotedb",
        remote_peers=[{"uid": "peer-a"}, {"uid": "peer-b"}],
    )
    captured = _capture_payload(service, monkeypatch, "shared_key")

    assert captured["payload"]["params"]["public_key_tokens"] == (
        "peer-a shared_key peer-b shared_key"
    )


@pytest.mark.parametrize(
    "peers, message",
    [
        ([{"uid": "peer-a"}, {"uid": "peer-a"}], "Duplicate remote peer UID"),
        ([{"uid": "peer-a"}, {}], r"remote_peers\[1\]\.uid"),
        ([], "must contain peers"),
    ],
)
def test_uploaded_key_rejects_invalid_remote_peer_uids(peers, message):
    service = _service(
        uid="federation",
        atomdb_type="remotedb",
        remote_peers=peers,
    )

    with pytest.raises(CustomValueError, match=message):
        service._build_public_key_tokens("shared_key")


def test_query_without_key_ignores_config_key_tokens(monkeypatch):
    service = _service()
    captured = {}
    monkeypatch.setattr(
        service,
        "_call_http_proxy",
        lambda method, path, **kwargs: captured.update(kwargs) or object(),
    )

    service.create_query_execution(
        "query", {"public_key_tokens": "legacy key", "count_flag": True}
    )

    assert "public_key_tokens" not in captured["json"]["params"]
    assert captured["json"]["params"]["count_flag"] is True


@pytest.mark.parametrize("invalid_key", ["", "  \n", "two tokens", "key\nsecond"])
def test_uploaded_key_must_contain_one_token(invalid_key):
    service = _service()

    with pytest.raises(CustomValueError, match="single non-empty token"):
        service._build_public_key_tokens(invalid_key)


def test_uploaded_key_requires_atomdb_uid():
    service = _service(uid="invalid uid")

    with pytest.raises(CustomValueError, match="atomdb.uid"):
        service._build_public_key_tokens("valid_key")


