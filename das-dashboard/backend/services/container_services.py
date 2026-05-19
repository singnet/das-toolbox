import subprocess
from typing import Dict, Any
import docker
from shared.exceptions.custom_exceptions import DasCliCommandException
from shared.enums.action_types import ActionTypes

class ContainerServices:
    def __init__(self):
        self.local_docker = docker.from_env()

    def _execute_local_action(self, container_name: str, action: str):
        try:
            container = self.local_docker.containers.get(container_name)
            if action == ActionTypes.START.value:
                container.start()
            elif action == ActionTypes.STOP.value:
                container.stop(timeout=0)
            elif action == ActionTypes.RESTART.value:
                container.restart(timeout=2)
            return True
        except docker.errors.NotFound:
            raise DasCliCommandException(f"Container {container_name} not found.", "Local error")
        except Exception as e:
            raise DasCliCommandException(f"Local Docker action failed: {str(e)}", "Docker error")

    def _execute_remote_action(self, service_name: str, action: str, target_info: Dict[str, Any]):
        service_parts = service_name.split()
        
        cmd = ["das-cli"] + service_parts + [action]

        cmd.extend([
            "--remote",
            "--host", target_info.get("ip"),
            "-u", target_info.get("username", "root"),
            "-k", target_info.get("key_file"),
            "-o", "json"
        ])

        try:

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr or e.stdout
            raise DasCliCommandException(f"Remote das-cli failed: {error_msg}", "Remote error")
        except Exception as e:
            raise DasCliCommandException(f"Failed to execute remote command: {str(e)}", "CLI error")

    def manage_container(self, action: Any, target_info: Dict[str, Any], container_name: str, service_name: str = None):
        ip = target_info.get("ip")
        action_str = action.value if hasattr(action, 'value') else action
        
        if ip in ("localhost", "0.0.0.0", "127.0.0.1"):
            return self._execute_local_action(container_name, action_str)
        
        target_service = service_name or container_name
        return self._execute_remote_action(target_service, action_str, target_info)