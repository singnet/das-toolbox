import os
import json
import docker
from exceptions import ContainerAlreadyRunningException, ContainerNotRunningException
from docker.errors import NotFound as ContainerNotFound

DEFAULT_CONTAINERS_PATH = os.path.expanduser("~/.das/containers.json")


class Container:
    def __init__(self, name, image=None, image_version="latest") -> None:
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

    def append_to_running_file(self, id: str, filename=DEFAULT_CONTAINERS_PATH):
        container_data = {
            "name": self._name,
            "id": id,
            "image": self.get_image(),
        }

        if os.path.exists(filename):
            with open(filename, "r") as json_file:
                data = json.load(json_file)
                if "running" in data:
                    data["running"].append(container_data)
                else:
                    data["running"] = [container_data]
        else:
            data = {"running": [container_data]}

        with open(filename, "w") as json_file:
            json.dump(data, json_file, indent=2)

    @staticmethod
    def remove_all_running(filename=DEFAULT_CONTAINERS_PATH):
        if os.path.exists(filename):
            with open(filename, "r") as json_file:
                data = json.load(json_file)
                if "running" in data:
                    data["running"] = []

            with open(filename, "w") as json_file:
                json.dump(data, json_file, indent=2)


class ContainerService:
    def __init__(self) -> None:
        self.docker_client = docker.from_env()
        self.redis = Container("das-redis", "redis", "7.2.3-alpine")
        self.mongodb = Container("das-mongodb", "mongo", "6.0.13-jammy")
        self.canonical_load = Container(
            "das-canonical-load",
            "levisingnet/canonical-load",
        )
        self.openfaas = Container("das-openfaas")

    def is_container_running(self, image: str) -> bool:
        containers = self.docker_client.containers.list(filters={"ancestor": image})
        return len(containers) > 0

    def setup_openfaas(
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
    ) -> str:
        function_full_version = f"v{version}-{function}"
        function_image = f"{repository}:{function_full_version}"

        if not self.is_container_running(
            self.redis.get_image()
        ) or not self.is_container_running(self.mongodb.get_image()):
            raise ContainerNotRunningException()

        if self.is_container_running(function_image):
            raise ContainerAlreadyRunningException(
                f"The FaaS container is alreday running"
            )

        self.openfaas.set_image(function_image)
        self.openfaas.set_image_version(function_full_version)

        docker_response = self.docker_client.containers.run(
            function_image,
            name=self.openfaas.get_name(),
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

        self.openfaas.append_to_running_file(docker_response.id)

        return docker_response.id

    def setup_redis(self, redis_port: int) -> str:
        if self.is_container_running(self.redis.get_image()):
            raise ContainerAlreadyRunningException()

        docker_response = self.docker_client.containers.run(
            self.redis.get_image(),
            name=self.redis.get_name(),
            detach=True,
            restart_policy={
                "Name": "on-failure",
                "MaximumRetryCount": 5,
            },
            ports={
                "6379/tcp": redis_port,
            },
        )

        self.redis.append_to_running_file(docker_response.id)

        return docker_response.id

    def setup_mongodb(
        self,
        mongodb_port: int,
        mongodb_username: str,
        mongodb_password: str,
    ) -> str:
        if self.is_container_running(self.mongodb.get_image()):
            raise ContainerAlreadyRunningException()

        docker_response = self.docker_client.containers.run(
            self.mongodb.get_image(),
            name=self.mongodb.get_name(),
            detach=True,
            restart_policy={
                "Name": "on-failure",
                "MaximumRetryCount": 5,
            },
            ports={
                "27017/tcp": mongodb_port,
            },
            environment={
                "MONGO_INITDB_ROOT_USERNAME": mongodb_username,
                "MONGO_INITDB_ROOT_PASSWORD": mongodb_password,
            },
        )

        self.mongodb.append_to_running_file(docker_response.id)

        return docker_response.id

    def setup_canonical_load(
        self,
        metta_path,
        canonical_flag,
        mongodb_port,
        mongodb_username,
        mongodb_password,
        redis_port,
    ) -> str:
        canonical = "--canonical" if canonical_flag else ""
        command = (
            f"python3 scripts/load_das.py {canonical} --knowledge-base {metta_path}"
        )

        if not self.is_container_running(
            self.redis.get_image()
        ) or not self.is_container_running(self.mongodb.get_image()):
            raise ContainerNotRunningException()

        if not os.path.exists(metta_path):
            raise FileNotFoundError()

        docker_response = self.docker_client.containers.run(
            self.canonical_load,
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

        self.canonical_load.append_to_running_file(docker_response.id)

        return docker_response.id

    # def stop(self, id) -> None:
    #     containers = [
    #         self.redis,
    #         self.canonical_load,
    #         self.mongodb,
    #         self.openfaas,
    #     ]

    #     for container in containers:
    #         try:
    #             if container.id == id:
    #                 docker_container = self.docker_client.containers.get(container.id)

    #                 docker_container.stop()
    #                 return
    #         except ContainerNotFound:
    #             pass

    def prune(self) -> None:
        # containers = [
        #     self.redis,
        #     self.canonical_load,
        #     self.mongodb,
        #     self.openfaas,
        # ]

        # for container in containers:
        #     try:
        #         docker_container = self.docker_client.containers.get(container.id)

        #         docker_container.stop()
        #     except ContainerNotFound:
        #         pass
        containers = self.docker_client.containers.list()

        for container in containers:
            container.stop()

        Container.remove_all_running()
