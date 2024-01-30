import docker


class EnvironmentService:
    def __init__(self) -> None:
        self.docker_client = docker.from_env()

    def setup_redis(self, redis_port: int) -> None:
        redis_container = self.docker_client.containers.run(
            "redis:7.2.3-alpine",
            detach=True,
            ports={
                "6379/tcp": redis_port,
            },
        )

    def setup_mongodb(self, mongodb_port: int) -> None:
        mongodb_container = self.docker_client.containers.run(
            "mongo:6.0.13-jammy",
            detach=True,
            ports={
                "27017/tcp": mongodb_port,
            },
        )

    def shutdown(self) -> None:
        containers = self.docker_client.containers.list()

        for container in containers:
            print(f"Parando container: {container.id}")
            container.stop()
