import subprocess

import docker

from shared.enums.action_types import ActionTypes
from shared.enums.das_services import DASServices
from shared.internal.web_configuration import WebConfiguration
from shared.exceptions.custom_exceptions import DasCliCommandException


LOCAL_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0"}


class ContainerServices:

    def __init__(self, web_config: WebConfiguration):
        self.local_docker = docker.from_env()
        self.web_config = web_config

    def _validate_return_error(self, return_stdout : str, return_stderr : str) -> bool:
        pass

    
    def _is_remote(self, host: str) -> bool:
        return host not in LOCAL_HOSTS

    def _resolve_query_peer(self):

        query = self.web_config.config_dictionary.get("query-agent")

        if not query:
            return None

        return {"host": query["host"], "port": query["port"]}

    def build_das_cli_command(self, host: str, service: DASServices, action: str):

        cmd = ["das-cli", service.value["command"], action]

        peer = self._resolve_query_peer()

        if service.value["requires_peer"] and peer and action != "stop":
            cmd.extend(["--peer-hostname", peer["host"], "--peer-port", str(peer["port"])])

        if self._is_remote(host):

            profile = self.web_config.user_profile

            cmd.extend([
                "--remote",
                "--host", host,
                "-u", profile.get("profile_username", "root"),
                "-k", profile.get("profile_ssh_keypath"),
            ])

        cmd.extend(["-o", "json"])

        return cmd

    def run_das_cli_command(self, command: list):

        try:

            result = subprocess.run(command, capture_output=True, text=True, check=True)

            return {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": command,
            }


        except subprocess.CalledProcessError as e:
            raise DasCliCommandException(e.stderr or e.stdout, "CLI error")

        except Exception as e:
            raise DasCliCommandException(str(e), "Execution error")

    def manage_container(self, host: str, action: ActionTypes, container_name: str = None, command : str = None):

        service : DASServices = None

        if command is None:
            service = DASServices.from_container(container_name)
        else:
            service = DASServices.from_command(command)

        command = self.build_das_cli_command(
            host=host,
            service=service,
            action=action.value,
        )

        return self.run_das_cli_command(command)
    
    def orchestrate_architecture(self, host: str, action: ActionTypes):
        
        results = []

        attention_broker_service = DASServices.from_command("attention-broker")
        query_agent_service = DASServices.from_command("query-agent")

        # Start these two as the DAS services have a dependency on them, so they are high priority.
        attention_broker_cmd = self.build_das_cli_command(host=host,service=attention_broker_service, action=action.value)
        query_agent_cmd = self.build_das_cli_command(host=host, service=query_agent_service, action=action.value)

        result_ab = self.run_das_cli_command(attention_broker_cmd)
        result_qa = self.run_das_cli_command(query_agent_cmd)

        results.extend([result_ab, result_qa])

        for key, value in self.web_config.config_dictionary.items():

            if key in ("attention-broker", "query-agent", "db"):
                continue
            
            service = DASServices.from_command(key)

            command = self.build_das_cli_command(host=host, service=service, action=action.value)
            result = self.run_das_cli_command(command)

            results.append(result)
        
        return results