import subprocess
from typing import List, Dict, AnyStr
from uuid import uuid4


class ContainerRemoteService:
    def __init__(self, servers: List[Dict]) -> None:
        self._servers = servers

    def create_context(self) -> List[AnyStr]:
        contexts = []

        for server in self._servers:
            errors = []
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

            contexts.append({
                "context": context_name,
                "ip": server_ip,
                "username": server_username,
            })

        return contexts
