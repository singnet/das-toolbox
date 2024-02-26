import os
import subprocess
from exceptions import ValidateFailed
from services.container_service import Container, ContainerService
from config import (
    METTA_LOADER_IMAGE_NAME,
    METTA_LOADER_IMAGE_VERSION,
    POC_LOADER_IMAGE_IMAGE_NAME,
    POC_LOADER_IMAGE_IMAGE_VERSION,
)


class PocLoaderContainerService(ContainerService):
    def __init__(
        self,
        loader_container_name,
        redis_container_name,
        mongodb_container_name,
    ) -> None:
        container = Container(
            loader_container_name,
            POC_LOADER_IMAGE_IMAGE_NAME,
            POC_LOADER_IMAGE_IMAGE_VERSION,
        )
        super().__init__(container)

        self.redis_container = Container(redis_container_name)
        self.mongodb_container = Container(mongodb_container_name)

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

        self.logs(container_id)

        return container_id


class MettaLoaderContainerService(ContainerService):
    def __init__(
        self,
        loader_container_name,
        redis_container_name,
        mongodb_container_name,
    ) -> None:
        container = Container(
            loader_container_name,
            METTA_LOADER_IMAGE_NAME,
            METTA_LOADER_IMAGE_VERSION,
        )
        self.redis_container = Container(redis_container_name)
        self.mongodb_container = Container(mongodb_container_name)

        super().__init__(container)

    def start_container(
        self,
        filepath,
        mongodb_port,
        mongodb_username,
        mongodb_password,
        redis_port,
    ):
        if not os.path.exists(filepath):
            raise FileNotFoundError()

        if not os.path.isfile(filepath):
            raise IsADirectoryError()

        docker_command = f"docker run --rm --net host --name {self.get_container().get_name()} -e DAS_REDIS_HOSTNAME=localhost -e DAS_REDIS_PORT={redis_port} -e DAS_MONGODB_HOSTNAME=localhost -e DAS_MONGODB_PORT={mongodb_port} -e DAS_MONGODB_USERNAME={mongodb_username} -e DAS_MONGODB_PASSWORD={mongodb_password} -i -v {os.path.dirname(filepath)}:/tmp {self.get_container().get_image()} db_loader {os.path.basename(filepath)}"
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
