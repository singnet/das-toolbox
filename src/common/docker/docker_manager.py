import docker
from typing import AnyStr, Union
from .exceptions import (
    DockerContextError,
    DockerDaemonConnectionError,
)


class DockerManager:
    def __init__(
        self,
        exec_context: Union[AnyStr, None] = None,
    ) -> None:
        self._exec_context = exec_context

    def set_exec_context(self, exec_context: Union[AnyStr]) -> None:
        self._exec_context = exec_context

    def _get_client(self, use: Union[AnyStr, None] = None) -> docker.DockerClient:
        context = docker.ContextAPI.get_context(use)
        if context is None:
            raise DockerContextError(f"Docker context {use!r} not found")
        try:
            return docker.DockerClient(
                base_url=context.endpoints["docker"]["Host"],
                use_ssh_client=True,
            )
        except Exception as e:
            raise e

    def get_docker_client(self) -> docker.DockerClient:
        try:
            return self._get_client(self._exec_context)
        except docker.errors.DockerException:
            raise DockerDaemonConnectionError(
                "Your Docker service appears to be either malfunctioning or not running."
            )
