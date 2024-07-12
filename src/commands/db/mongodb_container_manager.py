import json
import io
from common import Container, ContainerManager, ssh, get_rand_token
from config import MONGODB_IMAGE_NAME, MONGODB_IMAGE_VERSION
from typing import List, Dict, Union, AnyStr
from common.docker.exceptions import DockerError


class MongodbContainerManager(ContainerManager):
    _repl_set = "rs0"

    def __init__(self, mongodb_container_name) -> None:
        container = Container(
            mongodb_container_name,
            MONGODB_IMAGE_NAME,
            MONGODB_IMAGE_VERSION,
        )

        super().__init__(container)

    def _upload_key_to_server(self, cluster_node, mongodb_cluster_secret_key):
        keyfile_server_path = f"/tmp/{get_rand_token(num_bytes=5)}.txt"

        try:
            with ssh.open(cluster_node["host"], cluster_node["username"]) as (
                ssh_conn,
                sftp_conn,
            ):
                with sftp_conn.open(keyfile_server_path, "w") as remote_file:
                    remote_file.write(mongodb_cluster_secret_key.encode("utf-8"))

                ssh_conn.exec_command(f"chmod 400 {keyfile_server_path}")
                ssh_conn.exec_command(f"chown 999:999 {keyfile_server_path}")

            return keyfile_server_path

        except Exception as e:
            raise RuntimeError(
                f"Failed to upload key to server at {cluster_node['host']} (username: {cluster_node['username']}): {e}"
            )

    def _get_cluster_node_config(self, cluster_node, mongodb_cluster_secret_key):
        keyfile_path = "/data/keyfile.txt"
        keyfile_server_path = self._upload_key_to_server(
            cluster_node,
            mongodb_cluster_secret_key,
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
        mongodb_cluster_secret_key: Union[AnyStr, None] = None,
    ):
        self.raise_running_container()

        container = self._start_container(
            **self._get_cluster_node_config(cluster_node, mongodb_cluster_secret_key),
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
            healthcheck={
                "Test": ["CMD-SHELL", "mongosh --eval 'db.adminCommand(\"ping\")'"],
                "StartPeriod": 20000000,
            },
        )

        if not self.wait_for_container(container):
            raise DockerError("Timeout waiting for MongoDB container to start.")

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
        mongodb_username: str,
        mongodb_password: str,
    ):
        rl_config = self._get_replica_set_config(mongodb_port, mongodb_nodes)
        rl_config_json = json.dumps(rl_config)

        self.set_exec_context(mongodb_nodes[0]["context"])
        self._exec_container(
            f"mongosh -u {mongodb_username} -p {mongodb_password} --eval 'rs.initiate({rl_config_json})'"
        )
