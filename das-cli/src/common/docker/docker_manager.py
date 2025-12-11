import os
import platform
from typing import Union

import docker

from .exceptions import DockerContextError, DockerDaemonConnectionError


class DockerManager:
    _exec_context: Union[str, None]

    def __init__(self, exec_context: Union[str, None] = None) -> None:
        self.set_exec_context(exec_context)

    def unset_exec_context(self) -> None:
        self.set_exec_context(None)

    def set_exec_context(self, exec_context: Union[str, None] = None):
        self._exec_context = exec_context

    def _get_client(self, use: Union[str, None] = None) -> docker.DockerClient:
        system = platform.system()

        if use:
            try:
                context = docker.ContextAPI.get_context(use)
            except Exception:
                context = None

            if context is None:
                raise DockerContextError(f"Docker context {use} not found")

            host = None
            try:
                endpoints = context.endpoints
                docker_ep = endpoints.get("docker") or endpoints.get("Docker") or {}
                host = docker_ep.get("Host") or docker_ep.get("host") or docker_ep.get("Host")
            except Exception:
                host = None

            if host:
                try:
                    return docker.DockerClient(base_url=host)
                except docker.errors.DockerException:
                    raise DockerDaemonConnectionError(
                        f"Docker daemon for context '{use}' not reachable at {host}"
                    )

            try:
                prev_ctx = os.environ.get("DOCKER_CONTEXT")
                os.environ["DOCKER_CONTEXT"] = use
                try:
                    return docker.from_env()
                finally:
                    if prev_ctx is None:
                        os.environ.pop("DOCKER_CONTEXT", None)
                    else:
                        os.environ["DOCKER_CONTEXT"] = prev_ctx
            except docker.errors.DockerException:
                raise DockerDaemonConnectionError(
                    f"Docker context '{use}' found but client could not be created from environment"
                )

        if system != "Windows":
            try:
                return docker.from_env()
            except docker.errors.DockerException:
                raise DockerDaemonConnectionError("Docker daemon not reachable. Is Docker running?")

        try:
            return docker.DockerClient(base_url="npipe:////./pipe/docker_engine")
        except docker.errors.DockerException:
            pass

        try:
            return docker.DockerClient(base_url="tcp://127.0.0.1:2375")
        except docker.errors.DockerException:
            raise DockerDaemonConnectionError(
                "Docker daemon not reachable on Windows. "
                "Ensure Docker Desktop is running, or expose the daemon on tcp://localhost:2375."
            )

    def get_docker_client(self) -> docker.DockerClient:
        return self._get_client(self._exec_context)
