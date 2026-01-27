import socket
import time
from typing import Any, List, Optional, TypedDict, Union, cast

import docker
import docker.errors
from rich.console import Console
from rich.live import Live
from rich.panel import Panel

from common.exceptions import PortBindingError
from settings.config import SERVICES_NETWORK_NAME

from ..utils import deep_merge_dicts
from .docker_manager import DockerManager
from .exceptions import DockerContainerDuplicateError, DockerContainerNotFoundError, DockerError


class ContainerImageMetadata(TypedDict, total=False):
    name: str
    version: Optional[str]


class ContainerMetadata(TypedDict, total=False):
    port: Optional[int]
    image: ContainerImageMetadata


class Container:
    def __init__(self, name: str, metadata: ContainerMetadata) -> None:
        self._name = name
        self._metadata = metadata

    @property
    def port(self) -> int | None:
        return self._metadata.get("port")

    @property
    def name(self) -> str:
        return self._name

    @property
    def image(self) -> str:
        name = self._metadata["image"]["name"]
        version = self._metadata["image"].get("version", "latest")

        return f"{name}:{version}"

    @property
    def metadata(self) -> ContainerMetadata:
        return self._metadata

    def update_metadata(self, metadata: ContainerMetadata) -> None:
        merged_metadata = deep_merge_dicts(dict(self._metadata), dict(metadata))

        if "port" not in merged_metadata or "image" not in merged_metadata:
            raise ValueError("Merged metadata is missing required keys: 'port' and 'image'")

        self._metadata = ContainerMetadata(**cast(ContainerMetadata, merged_metadata))

    def __iter__(self):
        yield "name", self.name
        yield "port", self.port
        yield "image", self.image
        yield "metadata", self.metadata


class ContainerManager(DockerManager):
    def __init__(
        self,
        container: Container,
        exec_context: Union[str, None] = None,
    ) -> None:
        super().__init__(exec_context)
        self._container = container

    def get_container(self) -> Container:
        return self._container

    def _exec_container(self, command: str):
        try:
            container_name = self.get_container().name
            container = self.get_docker_client().containers.get(container_name)

            exec_result = container.exec_run(command, tty=True)

            if exec_result.exit_code != 0:
                raise DockerError(
                    f"Command '{command}' failed with exit code {exec_result.exit_code}. Output: {exec_result.output}"
                )

            return exec_result
        except docker.errors.APIError as e:
            raise DockerError(e.explanation)

    def _start_container(self, **kwargs) -> Any:
        self.raise_running_container()

        try:
            response = self.get_docker_client().containers.run(
                **kwargs,
                image=self.get_container().image,
                name=self.get_container().name,
                detach=True,
                network=SERVICES_NETWORK_NAME,
            )

            return response
        except docker.errors.APIError as e:
            raise DockerError(e.explanation)

    def raise_on_port_in_use(self, ports: List) -> None:
        for port in ports:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                port_in_use = s.connect_ex(("localhost", int(port))) == 0

                if port_in_use:
                    raise PortBindingError([port])

    def raise_running_container(self) -> None:
        if self.is_running():
            raise DockerContainerDuplicateError(
                "The Docker container is already running. Cannot start another container with the same name."
            )

    def is_running(self) -> bool | None:
        try:
            result = self.get_docker_client().containers.list(
                filters={"name": self._container.name}
            )

            return len(result) > 0
        except docker.errors.APIError as e:
            raise DockerError(e.explanation)

    def get_label(self, label: str) -> Union[dict, None]:
        container_name = self.get_container().name
        container = None

        try:
            container = self.get_docker_client().api.inspect_container(container_name)

            labels = container["Config"]["Labels"]

            return labels.get(
                label,
                None,
            )
        except docker.errors.APIError as e:
            raise DockerContainerNotFoundError(e.explanation)

    def status(self) -> dict:
        running = self.is_running()
        healthy = self.is_container_healthy(self.get_container()) if running else False
        return {
            "container_name": self._container.name,
            "image": self._container.image,
            "running": running,
            "healthy": healthy,
            "port": self._container.port,
        }

    def logs(self, follow: bool = False) -> None:
        container_name = self.get_container().name

        try:
            container = self.get_docker_client().containers.get(container_name)
        except docker.errors.NotFound:
            raise DockerError(f"Service {container_name} is not running")

        logs = container.logs(stdout=True, stderr=True, stream=True, follow=follow)

        for chunk in logs:
            if isinstance(chunk, (bytes, bytearray)):
                print(chunk.decode("utf-8", errors="ignore"), end="")
            else:
                print(chr(chunk), end="")

    def tail(self, file_path: str, clear_terminal: bool = False) -> None:
        console = Console()

        container_name = self.get_container().name
        container = self.get_docker_client().containers.get(container_name)

        exec_command = f"tail -f {file_path}"

        logs = container.exec_run(
            cmd=exec_command,
            tty=True,
            stdout=True,
            stderr=True,
            stream=True,
        )

        log_lines = []

        try:
            with Live(console=console, refresh_per_second=4) as live:
                for line in logs.output:
                    decoded_line = line.decode().strip()
                    if decoded_line != "":
                        log_lines.append(decoded_line)

                    panel_content = "\n".join(log_lines)
                    if clear_terminal:
                        panel_content = decoded_line

                    live.update(Panel(panel_content))
        except docker.errors.APIError:
            pass

    def prune_volumes(self) -> dict[str, Any]:
        client = self.get_docker_client()
        try:
            result = client.volumes.prune()
            return result
        except docker.errors.APIError as e:
            raise DockerError(f"Error pruning volumes: {e.explanation}")

    def stop(
        self,
        remove_volume: bool = False,
        force: bool = False,
    ) -> None:
        container_name = self.get_container().name
        container = None

        try:
            container = self.get_docker_client().containers.get(container_name)
        except docker.errors.APIError as e:
            raise DockerContainerNotFoundError(e.explanation)

        try:
            container.kill()
        # TODO: better exception handling, for now do not use bare except
        except Exception:
            pass

        try:
            container.remove(
                v=remove_volume,
                force=force,
            )
        except docker.errors.APIError as e:
            raise DockerError(e.explanation)

        if remove_volume:
            self.prune_volumes()

    def get_container_exit_status(self, container) -> int:
        try:
            return int(container.wait()["StatusCode"])
        except docker.errors.NotFound:
            exit_code = container.attrs["State"]["ExitCode"]
            return int(exit_code)

    def get_container_status(self, container) -> int:
        try:
            return int(container.attrs["State"]["ExitCode"])
        except docker.errors.NotFound:
            return -1

    def is_container_running(self, container) -> bool:
        status_code = self.get_container_status(container)
        return status_code == 0

    def is_container_healthy(self, container) -> bool:
        inspect_results = self.get_docker_client().api.inspect_container(container.name)
        health_status = inspect_results["State"].get("Health", {}).get("Status")

        if health_status is None:
            return True

        return str(health_status) == "healthy"

    def wait_for_container(self, container, timeout=60, interval=2) -> bool:
        elapsed_time = 0
        while elapsed_time < timeout:
            if self.is_container_running(container) and self.is_container_healthy(container):
                return True

            time.sleep(interval)
            elapsed_time += interval

        return False
