from services.container_service import Container, ContainerService


class OpenFaaSContainerService(ContainerService):
    def __init__(
        self,
        openfaas_container_name,
        redis_container_name,
        mongodb_container_name,
    ) -> None:
        container = Container(openfaas_container_name)
        super().__init__(container)

        self.redis_container = Container(redis_container_name)
        self.mongodb_container = Container(mongodb_container_name)

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
            network_mode="host",
            restart_policy={
                "Name": "on-failure",
                "MaximumRetryCount": 5,
            },
            environment={
                "exec_timeout": "30m",
                "service_timeout": "30m",
                "ack_wait": "30m",
                "read_timeout": "30m",
                "write_timeout": "30m",
                "exec_timeout": "30m",
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
