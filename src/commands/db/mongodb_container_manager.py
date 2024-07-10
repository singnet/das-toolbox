from common import Container, ContainerManager
from config import MONGODB_IMAGE_NAME, MONGODB_IMAGE_VERSION
from typing import AnyStr, List, Dict


class MongodbContainerManager(ContainerManager):
    def __init__(self, mongodb_container_name) -> None:
        container = Container(
            mongodb_container_name,
            MONGODB_IMAGE_NAME,
            MONGODB_IMAGE_VERSION,
        )

        super().__init__(container)

    def start_container(
        self,
        port: int,
        username: str,
        password: str,
    ):
        self.raise_running_container()

        container_id = self._start_container(
            command="--replSet rs0",
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

    def start_cluster(
        self,
        mongodb_nodes: List[Dict],
        mongodb_port: AnyStr,
    ):
        for index, mongodb_node in enumerate(mongodb_nodes):
            if index < 1:
                self._exec_container('mongo --eval "rs.initiate()"')
                continue

            server_ip = mongodb_node.get("ip")
            server_exec_context = mongodb_node.get("context")
            self.set_exec_context(server_exec_context)
            self._exec_container(
                f"mongo --eval \"rs.add('{server_ip}:{mongodb_port}')\""
            )
