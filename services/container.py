import docker


class ContainerService:
    def __init__(self) -> None:
        self.docker_client = docker.from_env()
        self.redis_image_name = "redis:7.2.3-alpine"
        self.mongodb_image_name = "mongo:6.0.13-jammy"

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

    def prune(self) -> None:
        containers = self.docker_client.containers.list()

        for container in containers:
            print(f"Parando container: {container.id}")
            container.stop()
