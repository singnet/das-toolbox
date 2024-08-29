import curses
import time
from typing import Any, AnyStr, Union

import docker
import docker.errors

from .docker_manager import DockerManager
from .exceptions import DockerContainerDuplicateError, DockerContainerNotFoundError, DockerError


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


class ContainerManager(DockerManager):
    def __init__(
        self,
        container: Container,
        exec_context: Union[AnyStr, None] = None,
    ) -> None:
        super().__init__(exec_context)
        self._container = container

    def get_container(self) -> Container:
        return self._container

    def _exec_container(self, command: str):
        try:
            container_name = self.get_container().get_name()
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
            result = self.get_docker_client().containers.list(filters={"name": container_name})

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
            container = self.get_docker_client().containers.get(self.get_container().get_name())
        except docker.errors.NotFound:
            raise DockerError(f"Service {self.get_container().get_name()} is not running")

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
        # TODO: better exception handling, for now do not use bare except
        except Exception:
            pass

        try:
            container.remove()
        except docker.errors.APIError as e:
            raise DockerError(e.explanation)

    def get_container_exit_status(self, container) -> int:
        try:
            return container.wait()["StatusCode"]
        except docker.errors.NotFound:
            container = self.get_docker_client().containers.get(container)
            exit_code = container.attrs["State"]["ExitCode"]
            return exit_code

    def get_container_status(self, container) -> int:
        try:
            return container.attrs["State"]["ExitCode"]
        except docker.errors.NotFound:
            return -1

    def is_container_running(self, container):
        status_code = self.get_container_status(container)
        return status_code == 0

    def is_container_healthy(self, container):
        inspect_results = self.get_docker_client().api.inspect_container(container.name)
        return inspect_results["State"]["Health"]["Status"] == "healthy"

    def wait_for_container(self, container, timeout=60, interval=2):
        elapsed_time = 0
        while elapsed_time < timeout:
            if self.is_container_running(container) and self.is_container_healthy(container):
                return True

            time.sleep(interval)
            elapsed_time += interval

        return False
