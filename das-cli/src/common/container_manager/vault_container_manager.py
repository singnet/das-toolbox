import time
from typing import Any, Dict

import docker

from common import Container, ContainerManager
from common.docker.exceptions import DockerContainerNotFoundError, DockerError
from http_json import HttpJsonError, request_json
from settings.config import DAS_PATH, OPENBAO_IMAGE_NAME, OPENBAO_IMAGE_VERSION

OPENBAO_CONFIG_DIR = DAS_PATH / "openbao"
OPENBAO_CONFIG_IN_CONTAINER = "/openbao/config"
OPENBAO_DATA_IN_CONTAINER = "/openbao/file"


class VaultContainerManager(ContainerManager):
    def __init__(
        self,
        vault_container_name: str,
        options: Dict = {},
    ) -> None:
        container = Container(
            vault_container_name,
            metadata={
                "port": options.get("vault_port"),
                "image": {
                    "name": OPENBAO_IMAGE_NAME,
                    "version": OPENBAO_IMAGE_VERSION,
                },
            },
        )

        self._options = options
        self._data_volume_name = f"{vault_container_name}-data"

        super().__init__(container)

    def start_container(self) -> None:
        self.raise_running_container()

        port = self._options.get("vault_port")
        if not isinstance(port, int):
            raise ValueError(
                "Invalid or missing vault.endpoint. Expected host:port with an integer port, "
                "for example 'localhost:8200'."
            )
        if not (1 <= port <= 65535):
            raise ValueError(
                f"Invalid vault.endpoint port '{port}'. Port must be between 1 and 65535."
            )
        self.raise_on_port_in_use([port])
        self._write_server_config(port)

        try:
            self._start_container(
                command=["bao", "server", f"-config={OPENBAO_CONFIG_IN_CONTAINER}"],
                cap_add=["IPC_LOCK"],
                restart_policy={
                    "Name": "on-failure",
                    "MaximumRetryCount": 5,
                },
                volumes={
                    str(OPENBAO_CONFIG_DIR): {
                        "bind": OPENBAO_CONFIG_IN_CONTAINER,
                        "mode": "ro",
                    },
                    self._data_volume_name: {
                        "bind": OPENBAO_DATA_IN_CONTAINER,
                        "mode": "rw",
                    },
                },
            )
        except docker.errors.APIError as e:
            raise DockerError(e.explanation)

        self.wait_for_api()

    def wait_for_api(self, timeout: int = 60, interval: float = 1) -> None:
        elapsed = 0.0
        while elapsed < timeout:
            self._raise_if_container_dead()
            try:
                self.get_status()
                return
            except DockerError:
                time.sleep(interval)
                elapsed += interval

        raise DockerError("Timeout waiting for the Vault API to become ready.")

    def _raise_if_container_dead(self) -> None:
        container_name = self.get_container().name
        try:
            container = self.get_docker_client().containers.get(container_name)
            container.reload()
            state = container.attrs.get("State", {})
            if state.get("Running") or state.get("Restarting"):
                return

            logs = container.logs(stdout=True, stderr=True, tail=50)
        except docker.errors.NotFound:
            raise DockerError(f"Vault container {container_name} is not running.")
        except docker.errors.APIError as error:
            raise DockerError(error.explanation or str(error))

        log_text = (
            logs.decode("utf-8", errors="replace").strip()
            if isinstance(logs, (bytes, bytearray))
            else str(logs).strip()
        )
        message = f"Vault container {container_name} stopped before the API became ready."
        if log_text:
            message = f"{message}\n{log_text}"
        raise DockerError(message)

    def get_status(self) -> dict[str, Any]:
        _status_code, payload = self._request("GET", "/v1/sys/seal-status")
        return payload

    def initialize(self) -> dict[str, Any]:
        _status_code, payload = self._request(
            "PUT",
            "/v1/sys/init",
            {
                "secret_shares": 3,
                "secret_threshold": 3,
            },
        )
        keys = payload.get("keys_base64") or payload.get("keys") or []
        root_token = payload.get("root_token")
        if not keys or not root_token:
            raise DockerError("Vault initialization did not return unseal keys and a root token.")

        return {
            "unseal_keys": keys,
            "root_token": root_token,
        }

    def unseal(self, key: str) -> dict[str, Any]:
        _status_code, payload = self._request("PUT", "/v1/sys/unseal", {"key": key})
        if payload.get("errors"):
            raise DockerError("; ".join(payload["errors"]))
        return payload

    def stop(
        self,
        remove_volume: bool = False,
        force: bool = False,
    ) -> None:
        missing_error = None
        try:
            super().stop(remove_volume=False, force=force)
        except DockerContainerNotFoundError as error:
            missing_error = error
            if not remove_volume:
                raise

        if remove_volume:
            self._remove_data_volume()

        if missing_error:
            raise missing_error

    def _write_server_config(self, port: int) -> None:
        OPENBAO_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        config_path = OPENBAO_CONFIG_DIR / "config.hcl"
        config_path.write_text(
            "\n".join(
                [
                    "ui = true",
                    "",
                    f'api_addr = "http://127.0.0.1:{port}"',
                    "",
                    'listener "tcp" {',
                    f'  address     = "0.0.0.0:{port}"',
                    "  tls_disable = true",
                    "}",
                    "",
                    'storage "file" {',
                    f'  path = "{OPENBAO_DATA_IN_CONTAINER}"',
                    "}",
                    "",
                ]
            ),
            encoding="utf-8",
        )

    def _remove_data_volume(self) -> None:
        try:
            volume = self.get_docker_client().volumes.get(self._data_volume_name)
            volume.remove(force=True)
        except docker.errors.NotFound:
            pass
        except docker.errors.APIError as e:
            raise DockerError(e.explanation)

    def _request(
        self,
        method: str,
        path: str,
        body: dict[str, Any] | None = None,
    ) -> tuple[int, dict[str, Any]]:
        port = self.get_container().port
        url = f"http://127.0.0.1:{port}{path}"
        try:
            return request_json(url, method, body)
        except HttpJsonError as error:
            raise DockerError(str(error)) from error.__cause__ or error
