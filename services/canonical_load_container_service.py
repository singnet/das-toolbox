import os
from services.container_service import Container, ContainerService
from config import CANONICAL_LOAD_IMAGE_NAME, CANONICAL_LOAD_IMAGE_VERSION


class CanonicalLoadContainerService(ContainerService):
    def __init__(
        self,
        canonical_load_container_name,
        redis_container_name,
        mongodb_container_name,
    ) -> None:
        container = Container(
            canonical_load_container_name,
            CANONICAL_LOAD_IMAGE_NAME,
            CANONICAL_LOAD_IMAGE_VERSION,
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
