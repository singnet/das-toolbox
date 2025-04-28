from typing import AnyStr, Dict, List, Union

from common import Container, ContainerManager
from common.network import is_server_port_available
from settings.config import REDIS_IMAGE_NAME, REDIS_IMAGE_VERSION


class RedisContainerManager(ContainerManager):
    def __init__(
        self,
        redis_container_name: str,
        options: Dict = {},
        exec_context: Union[str, None] = None,
    ) -> None:
        container = Container(
            redis_container_name,
            metadata={
                "port": options.get("redis_port"),
                "image": {
                    "name": REDIS_IMAGE_NAME,
                    "version": REDIS_IMAGE_VERSION,
                },
            },
        )

        super().__init__(container, exec_context)
        self._options = options

    @staticmethod
    def get_cluster_command_params(port: int) -> List[str]:
        return [
            "--cluster-enabled",
            "yes",
            "--cluster-config-file",
            "nodes.conf",
            "--cluster-node-timeout",
            "5000",
            "--bind",
            "0.0.0.0",
        ]

    def start_container(
        self,
        port: int,
        username: str,
        host: str,
        cluster: bool = False,
    ):
        self.raise_running_container()

        cluster_command_params = self.get_cluster_command_params(port) if cluster else []

        if cluster:
            is_server_port_available(
                username,
                host,
                port,
                port + 10000,
            )

        container_id = self._start_container(
            restart_policy={
                "Name": "on-failure",
                "MaximumRetryCount": 5,
            },
            command=[
                "redis-server",
                "--port",
                f"{port}",
                "--appendonly",
                "yes",
                "--protected-mode",
                "no",
                *cluster_command_params,
            ],
            ports={
                f"{port}/tcp": port,
                f"{port + 10000}/tcp": port + 10000
            },
        )

        return container_id

    def start_cluster(self, redis_nodes: List[Dict], redis_port: AnyStr):
        nodes_str = ""

        for redis_node in redis_nodes:
            server_ip = redis_node.get("ip")
            nodes_str += "{}:{} ".format(str(server_ip), str(redis_port))

        cmd = f"redis-cli --cluster create {nodes_str} --cluster-replicas 0 --cluster-yes"

        container_id = self._exec_container(cmd)

        return container_id

    def get_count_keys(self) -> dict:
        redis_port = self._options.get("redis_port")
        command = f"sh -c \"redis-cli -p {redis_port} KEYS '*' | cut -d ' ' -f2\""

        result = self._exec_container(command)

        redis_keys = result.output.split(b"\r\n")

        redis_keys_count: Dict = {}

        for key in redis_keys:
            prefix = key.decode().split(":")[0]

            if not key:
                continue

            redis_keys_count[prefix] = redis_keys_count.get(prefix, 0) + 1

        return redis_keys_count
