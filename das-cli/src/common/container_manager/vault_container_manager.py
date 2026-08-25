import os
from pathlib import Path
from typing import Dict

import docker

from common import Container, ContainerManager, get_rand_token
from common.docker.exceptions import DockerError
from settings.config import OPENBAO_IMAGE_NAME, OPENBAO_IMAGE_VERSION

OPENBAO_ENV_FILE = Path("/tmp/.openbao")
OPENBAO_ENV_FILE_IN_CONTAINER = "/tmp/.openbao"
OPENBAO_ENTRYPOINT = (
    "set -a; "
    f". {OPENBAO_ENV_FILE_IN_CONTAINER}; "
    "set +a; "
    "exec /usr/local/bin/docker-entrypoint.sh server -dev"
)


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

        super().__init__(container)

    def start_container(self) -> str:
        self.raise_running_container()

        port = int(self._options.get("vault_port", 0))
        self.raise_on_port_in_use([port])

        admin_password = get_rand_token(num_bytes=32)
        listen_address = f"0.0.0.0:{port}"

        fd = os.open(OPENBAO_ENV_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as env_file:
                env_file.write(f"BAO_DEV_ROOT_TOKEN_ID={admin_password}\n")
                env_file.write(f"BAO_DEV_LISTEN_ADDRESS={listen_address}\n")
                env_file.write("BAO_UI=true\n")
                env_file.write("SKIP_SETCAP=true\n")

            self._start_container(
                entrypoint=["/bin/sh", "-c", OPENBAO_ENTRYPOINT],
                command=[],
                cap_add=["IPC_LOCK"],
                restart_policy={
                    "Name": "on-failure",
                    "MaximumRetryCount": 5,
                },
                volumes={
                    str(OPENBAO_ENV_FILE): {
                        "bind": OPENBAO_ENV_FILE_IN_CONTAINER,
                        "mode": "ro",
                    }
                },
            )
        except docker.errors.APIError as e:
            OPENBAO_ENV_FILE.unlink(missing_ok=True)
            raise DockerError(e.explanation)
        except Exception:
            OPENBAO_ENV_FILE.unlink(missing_ok=True)
            raise

        return admin_password

    def stop(
        self,
        remove_volume: bool = False,
        force: bool = False,
    ) -> None:
        try:
            super().stop(remove_volume=remove_volume, force=force)
        finally:
            OPENBAO_ENV_FILE.unlink(missing_ok=True)
