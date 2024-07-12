import json
import io
from common import Container, ContainerManager, ssh, get_rand_token
from config import MONGODB_IMAGE_NAME, MONGODB_IMAGE_VERSION, SESSION_ID
from typing import AnyStr, List, Dict, Union


class MongodbContainerManager(ContainerManager):
    _repl_set = "rs0"

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
            remote_file = sftp_conn.open(file_path, "w")
            remote_file.write(content_stream.read())

            ssh_conn.exec_command(f"chmod 400 {file_path}")
            ssh_conn.exec_command(
                f"chown 999:999 {file_path}"
            )  # Inside the container 999 is the mongodb's uid and gid

    def _get_cluster_node_config(self, cluster_node):
        keyfile_server_path = "/tmp/" + get_rand_token(num_bytes=5) + ".txt"
        keyfile_path = "/data/keyfile.txt"

        self._generate_cluster_node_keyfile(
            **cluster_node,
            file_path=keyfile_server_path,
        )

        if not cluster_node:
            return {}
        return {
            "command": f"--replSet {self._repl_set} --keyFile {keyfile_path} --auth",
            "volumes": {
                keyfile_server_path: {
                    "bind": keyfile_path,
                    "mode": "ro",
                }
            },
        }

    def start_container(
        self,
        port: int,
        username: str,
        password: str,
        cluster_node: Union[Dict, None] = None,
    ):
        self.raise_running_container()

        container = self._start_container(
            **self._get_cluster_node_config(cluster_node),
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

        return container

    def _get_replica_set_config(
        self,
        mongodb_port: int,
        mongodb_nodes: List[Dict],
    ) -> dict:
        rs_config = {
            "_id": self._repl_set,
            "members": [],
        }

        for index, mongodb_node in enumerate(mongodb_nodes):
            mongodb_node_ip = mongodb_node["ip"]

            rs_config["members"].append(
                {
                    "_id": index,
                    "host": f"{mongodb_node_ip}:{mongodb_port}",
                }
            )

        return rs_config

    def start_cluster(
        self,
        mongodb_nodes: List[Dict],
        mongodb_port: int,
    ):
        rl_config = self._get_replica_set_config(mongodb_port, mongodb_nodes)
        rl_config_json = json.dumps(rl_config)

        print(rl_config_json)

        self.set_exec_context(mongodb_nodes[0]["context"])
        self._exec_container(f'bash -c "mongo --eval "rs.initiate({rl_config_json})""')
