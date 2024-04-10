import docker
from typing import Any, Union
from abc import ABC, abstractclassmethod
from exceptions import (
    ContainerAlreadyRunningException,
    NotFound,
    DockerException,
    DockerDaemonException,
)
import subprocess
import json
import curses


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

    def discovery(self):
        output = None

        docker_command = (
            f'docker ps --filter "name={self.get_name()}" --format "{{{{json . }}}}"'
        )

        try:
            output = subprocess.check_output(
                docker_command,
                shell=True,
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
        except subprocess.CalledProcessError:
            raise DockerException()

        try:
            return json.loads(output)
        except:
            return {}

    def is_running(self) -> bool:
        container = self.discovery()

        if container.get("Names") == self.get_name():
            return True

        return False

    def get_name(self) -> str:
        return self._name

    def get_image(self) -> str:
        return f"{self._image}:{self._image_version}"

    def set_image(self, image: str) -> None:
        self._image = image

    def set_image_version(self, image_version: str) -> None:
        self._image_version = image_version


class ContainerService(ABC):
    def __init__(self, container: Container) -> None:
        super().__init__()
        try:
            self._docker_client = docker.from_env()
        except docker.errors.DockerException:
            raise DockerDaemonException(
                "Your Docker service appears to be either malfunctioning or not running."
            )

        self._container = container

    def get_docker_client(self) -> docker.DockerClient:
        return self._docker_client

    def get_container(self) -> Container:
        return self._container

    def _start_container(self, **kwargs) -> Any:
        if self.get_container().is_running():
            raise ContainerAlreadyRunningException()

        response = self.get_docker_client().containers.run(
            **kwargs,
            image=self.get_container().get_image(),
            name=self.get_container().get_name(),
            detach=True,
        )

        return response

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
            raise NotFound()

    def logs(self) -> None:
        try:
            container = self.get_docker_client().containers.get(
                self.get_container().get_name()
            )
        except docker.errors.NotFound:
            raise DockerException(
                f"Service {self.get_container().get_name()} is not running"
            )

        for log in container.logs(stdout=True, stderr=True, stream=True):
            print(log.decode("utf-8"), end="")

    def tail(self, file_path: str, clear_terminal=False) -> None:
        container = self.get_docker_client().containers.get(
            self.get_container().get_name()
        )
        exec_command = f"tail -f {file_path}"
        logs = container.exec_run(
            cmd=exec_command,
            tty=True,
            stdout=True,
            stderr=True,
            stream=True,
        )

        stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)

        try:
            for line in logs.output:
                if clear_terminal:
                    stdscr.clear()

                if line.strip() != "":
                    stdscr.addstr(line.decode().strip() + "\n")

                stdscr.refresh()
        finally:
            curses.nocbreak()
            stdscr.keypad(False)
            curses.echo()
            curses.endwin()

    @classmethod
    def start_container(self, **config):
        pass

    def stop(self):
        container_name = self.get_container().get_name()
        container = None

        try:
            container = self.get_docker_client().containers.get(container_name)
        except docker.errors.APIError:
            raise NotFound()

        try:
            container.kill()
        except:
            pass

        try:
            container.remove()
        except docker.errors.APIError as e:
            # print(e.explanation) # TODO: ADD TO LOGGING FILE
            raise DockerException(e.explanation)
