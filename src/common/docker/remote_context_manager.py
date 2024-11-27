import subprocess
from typing import AnyStr, Dict, List
from uuid import uuid4


class RemoteContextManager:
    def __init__(
        self,
        servers: List[Dict] = [],
    ) -> None:
        self._servers = servers

    def _get_host(self, username: str, ip: str) -> str:
        return "ssh://{username}@{ip}".format(username=username, ip=ip)

    def _get_context(self, host: str) -> str:
        return f"host={host}"

    def set_servers(self, servers: List[Dict]) -> None:
        self._servers = servers

    def remove_context(self) -> Dict:
        failed = []

        for server in self._servers:
            server_context = server.get("context")

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
                    failed.append(server_context)
                    continue

        return failed

    def create_context(self) -> List[AnyStr]:
        contexts = []

        for server in self._servers:
            server_ip = server.get("ip")
            server_username = server.get("username")

            context_name = str(uuid4())
            context_description = (
                f"This context connects to {server_ip} and managed by das-cli"
            )
            context_host = self._get_host(server_username, server_ip)
            context_docker = self._get_context(
                host=context_host,
            )

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
                raise Exception(f"Could not create context for {server_ip}")

            contexts.append(
                {
                    "context": context_name,
                    "ip": server_ip,
                    "username": server_username,
                }
            )

        return contexts
