import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict

import docker

from shared.exceptions.custom_exceptions import DasCliCommandException
from shared.enums.action_types import ActionTypes

HOST_RUNTIME_BASE = "/opt/das-web/.das"
CONTAINER_RUNTIME_BASE = "/opt/das/.das"

class ContainerServices:
    def __init__(self):
        self.local_docker = docker.from_env()

    def _build_das_cli_command(
        self,
        service_name: str,
        action: str,
        target_info: Dict[str, Any],
    ) -> list:
        service_parts = service_name.split()

        cmd = ["das-cli"] + service_parts + [action]

        ip = target_info.get("ip")

        if ip not in ("localhost", "127.0.0.1", "0.0.0.0"):
            cmd.extend(
                [
                    "--remote",
                    "--host",
                    ip,
                    "-u",
                    target_info.get("username", "root"),
                    "-k",
                    target_info.get("key_file"),
                ]
            )

        cmd.extend(["-o", "json"])

        return cmd

    def _execute_das_cli(
        self,
        service_name: str,
        action: str,
        target_info: Dict[str, Any],
    ):
        try:
            cmd = self._build_das_cli_command(
                service_name,
                action,
                target_info,
            )

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
            )

            return {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": cmd,
            }

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr or e.stdout

            raise DasCliCommandException(f"das-cli failed: {error_msg}", "CLI error")

        except Exception as e:
            raise DasCliCommandException(f"Failed to execute das-cli: {str(e)}", "Execution error")

    def manage_container(
        self,
        action: ActionTypes,
        target_info: Dict[str, Any],
        service_name: str = None,
    ):

        return self._execute_das_cli(service_name, action, target_info)