import subprocess
import docker
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from shared.enums.action_types import ActionTypes
from shared.enums.das_services import DASServices
from shared.internal.web_configuration import WebConfiguration
from shared.internal.constants import DEFAULT_SSHKEY_CLONE_PATH, LOCAL_HOSTS
from shared.exceptions.custom_exceptions import DasCliCommandException, DASServiceInstantiationError, DASCLIResponseDecodeError


class ContainerServices:

    def __init__(self, web_config: WebConfiguration):
        self.local_docker = docker.from_env()
        self.web_config = web_config

    def manage_container(
        self,
        action: ActionTypes,
        container_name: str = None,
        command: str = None,
    ):
        if command is None:
            service = DASServices.from_container(container_name)
            host = self._resolve_service_host(service)
        else:
            service = DASServices.from_command(command)
            host = self._resolve_service_host(service)

        generated_command = self.build_das_cli_command(
            host=host,
            service=service,
            action=action.value,
        )
        return self.run_das_cli_command(generated_command)

    def orchestrate_architecture(self, action: ActionTypes):
        commands_to_run = {}
        has_local_command = False


        for cmd_name in ("attention-broker", "query-agent"):
            try:
                service = DASServices.from_command(cmd_name)
                host = self._resolve_service_host(service)
                if not self._is_remote(host):
                    has_local_command = True

                commands_to_run[cmd_name] = self.build_das_cli_command(
                    host=host, service=service, action=action.value
                )
            except DASServiceInstantiationError:
                continue


        for key in self.web_config.config_dictionary:
            if key in ("attention-broker", "query-agent", "db") or key in commands_to_run:
                continue
            try:
                service = DASServices.from_command(key)
                service_host = self._resolve_service_host(service)
                if not self._is_remote(service_host):
                    has_local_command = True

                commands_to_run[key] = self.build_das_cli_command(
                    host=service_host, service=service, action=action.value
                )
            except (DASServiceInstantiationError, ValueError):
                continue


        if has_local_command:
            return self._orchestrate_local(commands_to_run)
        
        return self._orchestrate_remote(commands_to_run)

    def _orchestrate_local(self, commands: dict) -> list:
        results = []
        errors = []

        for service_name, cmd in commands.items():
            try:
                data = self.run_das_cli_command(cmd)
                results.append(data)
            except Exception as exc:
                errors.append(f"Service {service_name} failed: {str(exc)}")

        if errors:
            raise DasCliCommandException(" | ".join(errors))

        return results

    def _orchestrate_remote(self, commands: dict) -> list:
        results = []
        errors = []

        with ThreadPoolExecutor(max_workers=min(len(commands) or 1, 12)) as executor:
            future_to_service = {
                executor.submit(self.run_das_cli_command, cmd): service_name 
                for service_name, cmd in commands.items()
            }

            for future in as_completed(future_to_service):
                service_name = future_to_service[future]
                try:
                    data = future.result()
                    results.append(data)
                except Exception as exc:
                    errors.append(f"Service {service_name} failed: {str(exc)}")

        if errors:
            raise DasCliCommandException(" | ".join(errors))

        return results

    def build_das_cli_command(self, host: str, service: DASServices, action: str):
        cmd = ["das-cli", service.value["command"], action]
        peer = self._resolve_query_peer()

        if service.value["requires_peer"] and peer and action != "stop":
            cmd.extend([
                "--peer-hostname", peer["host"],
                "--peer-port", str(peer["port"])
            ])

        if self._is_remote(host):
            profile = self.web_config.user_profile
            ssh_key = profile.get("profile_ssh_keypath") or DEFAULT_SSHKEY_CLONE_PATH
            cmd.extend([
                "--remote",
                "--host", host,
                "-u", profile.get("profile_username", "root"),
                "-k", ssh_key
            ])

        cmd.extend(["-o", "json"])
        return cmd

    def run_das_cli_command(self, command: list):
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
            )

            stdout_content = result.stdout
            stdout_json = json.loads(stdout_content.strip().replace("\n", ""))

            return {
                "success": True,
                "stdout": stdout_json,
                "stderr": result.stderr,
                "command": command,
            }

        except subprocess.CalledProcessError as e:
            error_output = (e.stderr or e.stdout or "Unknown Subprocess Error").strip()
            raise DasCliCommandException(error_output)

        except json.JSONDecodeError:
            raise DASCLIResponseDecodeError()

        except Exception as e:
            raise DasCliCommandException(str(e))

    def _resolve_service_host(self, service: DASServices) -> str:
        command = service.value["command"]
        service_config = self.web_config.config_dictionary.get(command)

        if not service_config:
            raise DASServiceInstantiationError()
        return service_config["host"]

    def _resolve_query_peer(self):
        query = self.web_config.config_dictionary.get("query-agent")
        if not query:
            return None
        return {
            "host": query["host"],
            "port": query["port"],
        }

    def _is_remote(self, host: str) -> bool:
        return host not in LOCAL_HOSTS