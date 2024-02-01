import docker
import os


class ContainerService:
    def __init__(self) -> None:
        self.docker_client = docker.from_env()
        self.redis_image_name = "redis:7.2.3-alpine"
        self.mongodb_image_name = "mongo:6.0.13-jammy"
        self.canonical_load = "levisingnet/canonical-load:latest"

    def is_redis_running(self):
        containers = self.docker_client.containers.list(
            filters={"ancestor": self.redis_image_name}
        )
        return len(containers) > 0

    def is_mongodb_running(self):
        containers = self.docker_client.containers.list(
            filters={"ancestor": self.mongodb_image_name}
        )
        return len(containers) > 0

    def setup_redis(self, redis_port: int) -> None:
        redis_container = self.docker_client.containers.run(
            self.redis_image_name,
            detach=True,
            restart_policy={
                "Name": "on-failure",
                "MaximumRetryCount": 5,
            },
            ports={
                "6379/tcp": redis_port,
            },
        )

        print(redis_container.id)

    def setup_mongodb(
        self,
        mongodb_port: int,
        mongodb_username: str,
        mongodb_password: str,
    ) -> None:
        mongodb_container = self.docker_client.containers.run(
            self.mongodb_image_name,
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

        print(mongodb_container.id)

    def setup_canonical_load(
        self,
        metta_path,
        canonical_flag,
        mongodb_port,
        mongodb_username,
        mongodb_password,
        redis_port,
    ) -> None:
        canonical = "--canonical" if canonical_flag else ""
        command = (
            f"python3 scripts/load_das.py {canonical} --knowledge-base {metta_path}"
        )

        if not os.path.exists(metta_path):
            raise FileNotFoundError(
                f"The specified path '{metta_path}' does not exist."
            )

        canonical_load_container = self.docker_client.containers.run(
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

        print(canonical_load_container.id)

    def prune(self) -> None:
        containers = self.docker_client.containers.list()

        for container in containers:
            print(f"Removing containers: {container.id}")
            container.stop()
