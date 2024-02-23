import docker
from typing import Any
from abc import ABC, abstractclassmethod
from exceptions import ContainerAlreadyRunningException
from config import ActiveServices
import subprocess


class Container:
    def __init__(
        self,
        name,
        image=None,
        image_version: str = "latest",
    ) -> None:
        self._container_config = ActiveServices()
        self._name = name

        container = self._check_running_container()

        if container is None:
            self._running = False
            self._id = None
            self._image = image
            self._image_version = image_version
        else:
            self._running = True
            self._id = container["id"]

            image_version = (
                container.get("image_version") if image is None else image_version
            )
            image = container["image"] if image is None else image

            self._image = image
            self._image_version = image_version

    def to_json(self) -> dict:
        return {
            "id": self.get_id(),
            "name": self.get_name(),
            "image": self.get_image(),
        }

    def get_container_config(self) -> ActiveServices:
        return self._container_config

    def _check_running_container(self) -> list:
        containers = self.get_container_config().get_content().get("running", [])

        for container in containers:
            if container["name"] == self.get_name():
                image, version = container["image"].split(":")
                return {
                    **container,
                    "image": image,
                    "image_version": version,
                }
        return None

    def container_running(self) -> bool:
        return self._running

    def get_id(self) -> str:
        return self._id

    def get_name(self) -> str:
        return self._name

    def get_image(self) -> str:
        return f"{self._image}:{self._image_version}"

    def set_id(self, id: str) -> None:
        self._id = id

    def set_image(self, image: str) -> None:
        self._image = image

    def set_image_version(self, image_version: str) -> None:
        self._image_version = image_version


class ContainerService(ABC):
    def __init__(self, container: Container) -> None:
        super().__init__()
        self._docker_client = docker.from_env()
        self._container = container

    def get_docker_client(self) -> docker.DockerClient:
        return self._docker_client

    def get_container(self) -> Container:
        return self._container

    def _start_container(self, **kwargs) -> Any:
        if self.get_container().container_running():
            raise ContainerAlreadyRunningException()

        response = self.get_docker_client().containers.run(
            **kwargs,
            image=self.get_container().get_image(),
            name=self.get_container().get_name(),
        )

        self.get_container().set_id(response.id)
        container_json = self.get_container().to_json()

        self.get_container().get_container_config().append_to_array(
            "running",
            container_json,
        ).save()

        return container_json["id"]

    def logs(self, container_id: str) -> None:
        container = self.get_docker_client().containers.get(container_id)

        for line in container.logs(stream=True):
            print(line)

    @abstractclassmethod
    def start_container(self, **config):
        pass

    def stop(self):
        container_json = self.get_container().to_json()

        docker_command = f"docker rm -f {self.get_container().get_name()}"

        subprocess.call(
            docker_command,
            shell=True,
            text=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        self.get_container().get_container_config().remove_from_array(
            "running",
            container_json,
        ).save()
