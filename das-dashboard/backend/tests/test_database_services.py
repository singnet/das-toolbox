import asyncio
from io import BytesIO

import pytest

from services.database_services import DatabaseServices
from shared.exceptions.custom_exceptions import CustomValueError, FileAlreadyExistsException


class _WebConfig:
    user_profile = {}

    def load_raw_configuration(self):
        raise AssertionError("MeTTa load must not use the dashboard configuration")


class _Upload:
    def __init__(self, name, data):
        self.filename = name
        self.file = BytesIO(data)
        self._data = data

    async def read(self):
        return self._data


def _service() -> DatabaseServices:
    return DatabaseServices(_WebConfig())


def test_host_cli_configuration_reads_config_list(monkeypatch):
    service = _service()

    def build(web_config, host, arguments):
        assert host == "10.1.0.8"
        assert arguments[:3] == ["config", "list", "-o"]
        return ["das-cli", *arguments]

    def run(cmd, **kwargs):
        assert cmd[:3] == ["das-cli", "config", "list"]
        return {"details": {"content": {"atomdb": {"type": "morkdb"}}}}

    monkeypatch.setattr("services.database_services.build_host_cli_command", build)
    monkeypatch.setattr("services.database_services.run_das_cli_json_command", run)

    assert service._host_cli_configuration("10.1.0.8")["atomdb"]["type"] == "morkdb"


def test_load_uses_target_cli_type_not_dashboard_config(monkeypatch):
    service = _service()
    monkeypatch.setattr(
        service,
        "_host_cli_configuration",
        lambda host: {"atomdb": {"type": "redismongodb"}},
    )
    monkeypatch.setattr(
        "services.database_services.build_host_cli_command",
        lambda *args: ["das-cli", "metta", "load"],
    )
    monkeypatch.setattr(
        "services.database_services.run_das_cli_json_command",
        lambda *args, **kwargs: {"status": "success"},
    )

    assert service.load_metta_file_into_db("10.1.0.8", "/tmp/kb.metta")["status"] == "success"


@pytest.mark.parametrize("atomdb_type", ["remotedb", "inmemorydb", "adapterdb"])
def test_load_and_upload_reject_blocked_target_types(monkeypatch, atomdb_type):
    service = _service()
    monkeypatch.setattr(
        service,
        "_host_cli_configuration",
        lambda host: {"atomdb": {"type": atomdb_type}},
    )
    monkeypatch.setattr(
        "services.database_services.run_das_cli_json_command",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("load should not run")),
    )

    with pytest.raises(CustomValueError):
        service.load_metta_file_into_db("localhost", "/tmp/kb.metta")

    with pytest.raises(CustomValueError):
        asyncio.run(service.save_metta_file("localhost", _Upload("kb.metta", b"()"), False))


def test_local_upload_reports_existing_local_path(tmp_path, monkeypatch):
    service = _service()
    monkeypatch.setattr(
        service,
        "_host_cli_configuration",
        lambda host: {"atomdb": {"type": "redismongodb"}},
    )
    monkeypatch.setattr("services.database_services.DEFAULT_METTA_FILES_PATH", str(tmp_path))
    existing = tmp_path / "kb.metta"
    existing.write_text("already")

    with pytest.raises(FileAlreadyExistsException) as error:
        asyncio.run(service.save_metta_file("localhost", _Upload("kb.metta", b"new"), False))

    assert error.value.file_path == str(existing)


def test_remote_upload_ignores_local_file_and_uses_remote_path(tmp_path, monkeypatch):
    service = _service()
    monkeypatch.setattr(
        service,
        "_host_cli_configuration",
        lambda host: {"atomdb": {"type": "redismongodb"}},
    )
    monkeypatch.setattr("services.database_services.DEFAULT_METTA_FILES_PATH", str(tmp_path))
    (tmp_path / "kb.metta").write_text("local only")

    class _Scp:
        def connect(self, host):
            assert host == "10.1.0.8"
            return type("SSH", (), {"close": lambda self: None})()

        def get_remote_home(self, ssh):
            return "/home/das"

        def ensure_remote_dir(self, ssh, remote_dir):
            assert remote_dir.startswith("/home/das")

        def remote_file_exists(self, ssh, remote_path):
            assert remote_path == "/home/das/.das/workspace/metta_files/kb.metta"
            return True

    service.remote_scp = _Scp()

    with pytest.raises(FileAlreadyExistsException) as error:
        asyncio.run(service.save_metta_file("10.1.0.8", _Upload("kb.metta", b"new"), False))

    assert error.value.file_path == "/home/das/.das/workspace/metta_files/kb.metta"


def test_remote_upload_writes_when_remote_file_is_missing(monkeypatch):
    service = _service()
    monkeypatch.setattr(
        service,
        "_host_cli_configuration",
        lambda host: {"atomdb": {"type": "morkdb"}},
    )
    written = {}

    class _Scp:
        def connect(self, host):
            return type("SSH", (), {
                "get_transport": lambda self: object(),
                "close": lambda self: None,
            })()

        def get_remote_home(self, ssh):
            return "/home/das"

        def ensure_remote_dir(self, ssh, remote_dir):
            written["dir"] = remote_dir

        def remote_file_exists(self, ssh, remote_path):
            return False

    service.remote_scp = _Scp()

    class _Client:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def putfo(self, file_obj, remote_path):
            written["path"] = remote_path
            written["body"] = file_obj.read()

    monkeypatch.setattr(
        "services.database_services.SCPClient",
        lambda transport: _Client(),
    )

    saved = asyncio.run(service.save_metta_file("10.1.0.8", _Upload("kb.metta", b"atoms"), False))

    assert saved == "/home/das/.das/workspace/metta_files/kb.metta"
    assert written["body"] == b"atoms"
