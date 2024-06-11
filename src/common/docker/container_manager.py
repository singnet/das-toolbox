import docker
import curses
from typing import Any, Union, AnyStr
from abc import ABC, abstractmethod

import docker.errors

from .exceptions import (
    DockerContainerDuplicateError,
    DockerContextError,
    DockerError,
    DockerDaemonConnectionError,
    DockerContainerNotFoundError,
)


class Container:
    def __init__(
        self,
        name,
        image=None,
        image_version: str = "latest",
    ) -> None:
        self._name = name
        self._image = image
        self._image_version = image_version

    def get_name(self) -> str:
        return self._name

    def get_image(self) -> str:
        return f"{self._image}:{self._image_version}"

    def set_image(self, image: str) -> None:
        self._image = image

    def set_image_version(self, image_version: str) -> None:
        self._image_version = image_version


class ContainerManager(ABC):
    def __init__(
        self,
        container: Container,
        exec_context: Union[AnyStr, None] = None,
    ) -> None:
        super().__init__()
        try:
            self._docker_client = self._get_client(exec_context)
        except docker.errors.DockerException:
            raise DockerDaemonConnectionError(
                "Your Docker service appears to be either malfunctioning or not running."
            )

        self._container = container

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
        return self._docker_client

    def get_container(self) -> Container:
        return self._container

    def _exec_container(self, command: str):
        try:
            container_name = self.get_container().get_name()
            container = self.get_docker_client().containers.get(container_name)

            return container.exec_run(command, tty=True)
        except docker.errors.APIError as e:
            raise DockerError(e.explanation)

    def _start_container(self, **kwargs) -> Any:
        self.raise_running_container()

        try:
            response = self.get_docker_client().containers.run(
                **kwargs,
                image=self.get_container().get_image(),
                name=self.get_container().get_name(),
                detach=True,
            )

            return response
        except docker.errors.APIError as e:
            raise DockerError(e.explanation)

    def raise_running_container(self):
        if self.is_running():
            raise DockerContainerDuplicateError()

    def is_running(self):
        container_name = self._container.get_name()

        try:
            result = self.get_docker_client().containers.list(
                filters={"name": container_name}
            )

            return len(result) > 0
        except docker.errors.APIError:
            raise DockerError()

    def get_label(self, label: str) -> Union[dict, None]:
        container_name = self.get_container().get_name()
        container = None

        try:
            container = self.get_docker_client().api.inspect_container(container_name)

            labels = container["Config"]["Labels"]

            return labels.get(
                label,
                None,
            )
        except docker.errors.APIError:
            raise DockerContainerNotFoundError()

    def logs(self) -> None:
        try:
            container = self.get_docker_client().containers.get(
                self.get_container().get_name()
            )
        except docker.errors.NotFound:
            raise DockerError(
                f"Service {self.get_container().get_name()} is not running"
            )

        for log in container.logs(stdout=True, stderr=True, stream=True):
            print(log.decode("utf-8"), end="")

    def tail(self, file_path: str, clear_terminal=False) -> None:
        container_name = self.get_container().get_name()

        stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)

        try:
            container = self.get_docker_client().containers.get(container_name)

            exec_command = f"tail -f {file_path}"

            logs = container.exec_run(
                cmd=exec_command,
                tty=True,
                stdout=True,
                stderr=True,
                stream=True,
            )

            for line in logs.output:
                if clear_terminal:
                    stdscr.clear()

                if line.strip() != "":
                    stdscr.addstr(line.decode().strip() + "\n")

                stdscr.refresh()

        except docker.errors.APIError:
            pass
        finally:
            curses.nocbreak()
            stdscr.keypad(False)
            curses.echo()
            curses.endwin()

    @abstractmethod
    def start_container(self, **config):
        pass

    def stop(self):
        container_name = self.get_container().get_name()
        container = None

        try:
            container = self.get_docker_client().containers.get(container_name)
        except docker.errors.APIError:
            raise DockerContainerNotFoundError()

        try:
            container.kill()
        except:
            pass

        try:
            container.remove()
        except docker.errors.APIError as e:
            raise DockerError(e.explanation)

    def container_status(self, container) -> int:
        try:
            return container.wait()["StatusCode"]
        except docker.errors.NotFound:
            container = self.get_docker_client().containers.get(container)
            exit_code = container.attrs["State"]["ExitCode"]
            return exit_code
