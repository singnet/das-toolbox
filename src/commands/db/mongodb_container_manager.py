import os
import io
from common import Container, ContainerManager, ssh
from config import MONGODB_IMAGE_NAME, MONGODB_IMAGE_VERSION, SESSION_ID
from typing import AnyStr, List, Dict, Union


class MongodbContainerManager(ContainerManager):
    def __init__(self, mongodb_container_name) -> None:
        container = Container(
            mongodb_container_name,
            MONGODB_IMAGE_NAME,
            MONGODB_IMAGE_VERSION,
        )

        super().__init__(container)

    def _generate_cluster_node_keyfile(self, host: str, username: str, file_path: str):
        with ssh.open(host, username) as (ssh_conn, sftp_conn):
            content_stream = io.BytesIO(SESSION_ID.encode("utf-8"))
            remote_file = sftp_conn.file(file_path, "w")
            remote_file.write(content_stream.read())

            ssh_conn.exec_command(f"chmod 400 {file_path}")

    def _setup_cluster_node_config(self, cluster_node: dict):
        keyfile_path = "/tmp/keyfile"

        self._generate_cluster_node_keyfile(**cluster_node, file_path=keyfile_path)

        return dict(
            command="mongod --replSet rs0",
            volumes={
                keyfile_path: {
                    "bind": "/data/keyfile",
                    "mode": "ro",
                },
            },
        )

    def start_container(
        self,
        port: int,
        username: str,
        password: str,
        cluster_node: Union[Dict, None] = None,
    ):
        self.raise_running_container()
        cluster_node_config = (
            self._setup_cluster_node_config(cluster_node) if cluster_node else {}
        )

        container_id = self._start_container(
            **cluster_node_config,
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
