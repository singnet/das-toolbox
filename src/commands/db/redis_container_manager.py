from typing import AnyStr, Dict, List, Union

from common import Container, ContainerManager
from config import REDIS_IMAGE_NAME, REDIS_IMAGE_VERSION


class RedisContainerManager(ContainerManager):
    def __init__(
        self,
        redis_container_name,
        exec_context: Union[AnyStr, None] = None,
    ) -> None:
        container = Container(
            redis_container_name,
            REDIS_IMAGE_NAME,
            REDIS_IMAGE_VERSION,
        )

        super().__init__(container, exec_context)

    def start_container(
        self,
        port: int,
        cluster: bool = False,
    ):
        self.raise_running_container()

        command_params = [
            "redis-server",
            "--port",
            f"{port}",
            "--appendonly",
            "yes",
            "--protected-mode",
            "no",
        ]

        if cluster:
            command_params += [
                "--cluster-enabled",
                "yes",
                "--cluster-config-file",
                "nodes.conf",
                "--cluster-node-timeout",
                "5000",
            ]

        container_id = self._start_container(
            restart_policy={
                "Name": "on-failure",
                "MaximumRetryCount": 5,
            },
            command=command_params,
            network_mode="host",
        )

        return container_id

    def start_cluster(self, redis_nodes: List[Dict], redis_port: AnyStr):
        nodes_str = ""

        for redis_node in redis_nodes:
            server_ip = redis_node.get("ip")
            nodes_str += f"{server_ip}:{redis_port} "

        cmd = f"redis-cli --cluster create {nodes_str} --cluster-replicas 0 --cluster-yes"

        container_id = self._exec_container(cmd)

        return container_id
