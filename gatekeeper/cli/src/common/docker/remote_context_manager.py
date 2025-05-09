import subprocess
from enum import Enum
from typing import Dict, List, TypedDict, Union, cast
from uuid import uuid4


class Server(TypedDict):
    ip: str
    username: str


class ServerContext(TypedDict):
    name: str
    description: str
    docker_host: str
    server_info: Server


class ServerContextAction(Enum):
    CREATE = "create"
    REMOVE = "remove"


class ServerContextEvent(TypedDict):
    type: ServerContextAction
    data: Union[ServerContext, List[str]]


class RemoteContextManager:
    _events: List[ServerContextEvent] = []

    @staticmethod
    def _get_host(username: str, ip: str) -> str:
        return "ssh://{username}@{ip}".format(username=username, ip=ip)

    @staticmethod
    def _get_context(host: str) -> str:
        return f"host={host}"

    def commit(self) -> None:
        for event in self._events:
            if event["type"] == ServerContextAction.CREATE:
                self._create_context(cast(ServerContext, event["data"]))
            elif event["type"] == ServerContextAction.REMOVE:
                self._remove_context(cast(List[str], event["data"]))

        self._events.clear()

    def _create_context(self, context: ServerContext) -> None:
        status_code = subprocess.call(
            [
                "docker",
                "context",
                "create",
                context["name"],
                "--description",
                context["description"],
                "--docker",
                context["docker_host"],
            ],
        )

        if status_code != 0:
            raise Exception(f"Could not create context for {context['server_info']['ip']}")

    def _remove_context(self, context_names: List[str]) -> None:
        for context_name in context_names:
            if context_name and context_name != "default":
                status_code = subprocess.call(
                    [
                        "docker",
                        "context",
                        "rm",
                        context_name,
                    ],
                )

                if status_code != 0:
                    raise Exception(f"Context {context_name} could not be removed from docker")

    def remove_servers_context(self, server_contexts: List[str]):
        self._events.append(
            ServerContextEvent({"type": ServerContextAction.REMOVE, "data": server_contexts})
        )

    def create_servers_context(self, servers: List[Server]) -> List[Dict]:
        contexts: List[Dict] = []

        for server in servers:
            server_ip = server.get("ip", "")
            server_username = server.get("username", "")
            context_name = str(uuid4())
            context_description = f"This context connects to {server_ip} and managed by das-cli"
            context_host = RemoteContextManager._get_host(server_username, server_ip)
            context_docker = RemoteContextManager._get_context(host=context_host)
            event = ServerContextEvent(
                {
                    "type": ServerContextAction.CREATE,
                    "data": ServerContext(
                        {
                            "name": context_name,
                            "description": context_description,
                            "server_info": Server(
                                {
                                    "username": server_username,
                                    "ip": server_ip,
                                }
                            ),
                            "docker_host": context_docker,
                        }
                    ),
                }
            )

            self._events.append(event)
            server_info = cast(ServerContext, event["data"])["server_info"]
            contexts.append(
                {
                    "context": context_name,
                    **server_info,
                },
            )

        return contexts
