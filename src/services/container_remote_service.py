import subprocess
from typing import List, Dict, AnyStr
from uuid import uuid4


class ContainerRemoteService:
    def __init__(self, servers: List[Dict]) -> None:
        self._servers = servers

    def remove_context(self) -> Dict:
        errors = []

        for server in self._servers:
            server_context = server.get("context")
            server_ip = server.get("ip")

            if server_context and server_context != "default":
                status_code = subprocess.call(
                    [
                        "docker",
                        "context",
                        "rm",
                        server_context,
                    ],
                )

                if status_code != 0:
                    errors.append(f"Could not create context for {server_ip}")
                    continue

        return errors

    def create_context(self) -> List[AnyStr]:
        contexts = []
        errors = []

        for server in self._servers:
            server_ip = server.get("ip")
            server_username = server.get("username")

            context_name = str(uuid4())
            context_description = (
                f"This context connects to {server_ip} and managed by das-cli"
            )
            context_docker = f"host=ssh://{server_username}@{server_ip}"

            status_code = subprocess.call(
                [
                    "docker",
                    "context",
                    "create",
                    context_name,
                    "--description",
                    context_description,
                    "--docker",
                    context_docker,
                ],
            )

            if status_code != 0:
                errors.append(f"Could not create context for {server_ip}")
                continue

            contexts.append(
                {
                    "context": context_name,
                    "ip": server_ip,
                    "username": server_username,
                }
            )

        return contexts
