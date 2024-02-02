import docker
import os
from typing import Any
from abc import ABC, abstractclassmethod
from exceptions import ContainerAlreadyRunningException, ValidateFailed
from config import ContainerConfig
from docker.errors import NotFound
import subprocess


class Container:
    def __init__(
        self,
        name,
        image=None,
        image_version: str = "latest",
    ) -> None:
        self._container_config = ContainerConfig()
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

    def get_container_config(self) -> ContainerConfig:
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

    @abstractclassmethod
    def start_container(self, **config):
        pass

    def stop(self):
        container_json = self.get_container().to_json()

        if not self.get_container().container_running():
            return None

        try:
            container = self.get_docker_client().containers.get(
                container_id=container_json["id"]
            )

            container.remove(force=True)
        except NotFound:
            pass

        self.get_container().get_container_config().remove_from_array(
            "running",
            container_json,
        ).save()


class RedisContainerService(ContainerService):
    def __init__(self) -> None:
        container = Container("das-redis", "redis", "7.2.3-alpine")

        super().__init__(container)

    def start_container(self, port: int):
        container_id = self._start_container(
            detach=True,
            restart_policy={
                "Name": "on-failure",
                "MaximumRetryCount": 5,
            },
            ports={
                "6379/tcp": port,
            },
        )

        return container_id


class MongoContainerService(ContainerService):
    def __init__(self) -> None:
        container = Container("das-mongodb", "mongo", "6.0.13-jammy")

        super().__init__(container)

    def start_container(self, port: int, username: str, password: str):
        container_id = self._start_container(
            detach=True,
            restart_policy={
                "Name": "on-failure",
                "MaximumRetryCount": 5,
            },
            ports={
                "27017/tcp": port,
            },
            environment={
                "MONGO_INITDB_ROOT_USERNAME": username,
                "MONGO_INITDB_ROOT_PASSWORD": password,
            },
        )

        return container_id


class CanonicalLoadContainerService(ContainerService):
    def __init__(self) -> None:
        container = Container(
            "das-canonical-load",
            "levisingnet/canonical-load",
        )
        super().__init__(container)

        self.redis_container = Container("das-redis")
        self.mongodb_container = Container("das-mongodb")

    def start_container(
        self,
        metta_path,
        canonical_flag,
        mongodb_port,
        mongodb_username,
        mongodb_password,
        redis_port,
    ):
        canonical = "--canonical" if canonical_flag else ""
        command = (
            f"python3 scripts/load_das.py {canonical} --knowledge-base {metta_path}"
        )

        if not os.path.exists(metta_path):
            raise FileNotFoundError()

        container_id = self._start_container(
            detach=True,
            command=command,
            network_mode="host",
            volumes={
                metta_path: {
                    "bind": metta_path,
                    "mode": "rw",
                },
            },
            restart_policy={
                "Name": "on-failure",
                "MaximumRetryCount": 5,
            },
            environment={
                "DAS_MONGODB_PORT": mongodb_port,
                "DAS_REDIS_PORT": redis_port,
                "DAS_DATABASE_USERNAME": mongodb_username,
                "DAS_DATABASE_PASSWORD": mongodb_password,
                "DAS_MONGODB_HOSTNAME": "localhost",
                "DAS_REDIS_HOSTNAME": "localhost",
                "DAS_MONGODB_NAME": "das",
                "PYTHONPATH": "/app",
                "DAS_KNOWLEDGE_BASE": metta_path,
            },
        )

        return container_id


class OpenFaaSContainerService(ContainerService):
    def __init__(self) -> None:
        container = Container("das-openfaas")
        super().__init__(container)

        self.redis_container = Container("das-redis")
        self.mongodb_container = Container("das-mongodb")

    def start_container(
        self,
        repository: str,
        function: str,
        version: str,
        external_port: int,
        redis_port: int,
        mongodb_port: int,
        mongodb_username: str,
        mongodb_password: str,
        internal_port: int = 8080,
    ):
        function_version = f"v{version}-{function}"

        self.get_container().set_image(repository)
        self.get_container().set_image_version(function_version)

        container_id = self._start_container(
            detach=True,
            network_mode="host",
            restart_policy={
                "Name": "on-failure",
                "MaximumRetryCount": 5,
            },
            environment={
                "DAS_MONGODB_HOSTNAME": "localhost",
                "DAS_REDIS_HOSTNAME": "localhost",
                "DAS_MONGODB_NAME": "das",
                "DAS_MONGODB_PASSWORD": mongodb_password,
                "DAS_MONGODB_PORT": mongodb_port,
                "DAS_MONGODB_USERNAME": mongodb_username,
                "DAS_REDIS_PORT": redis_port,
            },
        )

        return container_id


class MettaParserContainerService(ContainerService):
    def __init__(self) -> None:
        container = Container(
            "das-metta-parser", "levisingnet/das-metta-parser", "latest"
        )

        super().__init__(container)

    def start_container(self, filepath):
        docker_command = f"docker run --rm --name {self.get_container().get_name()} -i {self.get_container().get_image()} < {filepath}"
        exit_code = subprocess.call(
            docker_command,
            shell=True,
            text=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        if exit_code > 0:
            raise ValidateFailed()

        return None
