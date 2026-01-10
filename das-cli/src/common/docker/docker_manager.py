import os
import platform
from typing import Union

import docker


class DockerManager:
    _exec_context: Union[str, None]

    def __init__(self, exec_context: Union[str, None] = None) -> None:
        self.set_exec_context(exec_context)

    def unset_exec_context(self) -> None:
        self.set_exec_context(None)

    def set_exec_context(self, exec_context: Union[str, None] = None):
        self._exec_context = exec_context

    def _get_client(self, use: Union[str, None] = None) -> docker.DockerClient:
        if not use or use.lower() == "default":
            try:
                return docker.from_env()
            except Exception:
                if platform.system() == "Windows":
                    return docker.DockerClient(base_url="npipe:////./pipe/docker_engine")
                raise

        try:
            context = docker.ContextAPI.get_context(use)
            if context:
                endpoints = context.endpoints
                docker_ep = endpoints.get("docker") or endpoints.get("Docker") or {}
                host = docker_ep.get("Host") or docker_ep.get("host")

                if host:
                    return docker.DockerClient(base_url=host)
        except Exception:
            pass

        try:
            original_ctx = os.environ.get("DOCKER_CONTEXT")
            os.environ["DOCKER_CONTEXT"] = use
            client = docker.from_env()
            client.ping()
            return client
        except Exception as e:
            raise Exception(f"Não foi possível conectar ao contexto {use}: {e}")
        finally:
            if original_ctx:
                os.environ["DOCKER_CONTEXT"] = original_ctx
            else:
                os.environ.pop("DOCKER_CONTEXT", None)

    def get_docker_client(self) -> docker.DockerClient:
        return self._get_client(self._exec_context)
