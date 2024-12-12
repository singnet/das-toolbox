import io
import json
from typing import AnyStr, Dict, List, Union

from common import Container, ContainerManager, get_rand_token, ssh
from common.docker.exceptions import DockerError
from config import MONGODB_IMAGE_NAME, MONGODB_IMAGE_VERSION


class MongodbContainerManager(ContainerManager):
    _repl_set = "rs0"

    def __init__(
        self,
        mongodb_container_name: str,
        options: Dict = {},
    ) -> None:
        container = Container(
            mongodb_container_name,
            metadata={
                "port": options.get("mongodb_port"),
                "image": {
                    "name": MONGODB_IMAGE_NAME,
                    "version": MONGODB_IMAGE_VERSION,
                },
            },
        )

        super().__init__(container)
        self._options = options

    def _upload_key_to_server(self, cluster_node, mongodb_cluster_secret_key):
        keyfile_server_path = f"/tmp/{get_rand_token(num_bytes=5)}.txt"

        try:
            with ssh.open(cluster_node["host"], cluster_node["username"]) as (
                ssh_conn,
                sftp_conn,
            ):
                content_stream = io.BytesIO(mongodb_cluster_secret_key.encode("utf-8"))
                remote_file = sftp_conn.open(keyfile_server_path, "w")
                remote_file.write(content_stream.read())

                ssh_conn.exec_command(f"chmod 400 {keyfile_server_path}")
                ssh_conn.exec_command(
                    f"chown 999:999 {keyfile_server_path}"
                )  # Inside the container 999 is the mongodb's uid and gid

            return keyfile_server_path

        except Exception as e:
            raise RuntimeError(
                f"Failed to upload key to server at {cluster_node['host']} (username: {cluster_node['username']}): {e}"
            )

    def _get_cluster_node_config(self, cluster_node, mongodb_cluster_secret_key):
        if not cluster_node:
            return {}

        keyfile_path = "/data/keyfile.txt"
        keyfile_server_path = self._upload_key_to_server(
            cluster_node,
            mongodb_cluster_secret_key,
        )

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

    def get_collection_stats(self) -> dict:
        mongodb_username = self._options.get("mongodb_username")
        mongodb_password = self._options.get("mongodb_password")

        mongodb_command = "JSON.stringify({ atoms: db.atoms.countDocuments(), nodes: db.atoms.countDocuments({ composite_type: { $exists: false } }), links: db.atoms.countDocuments({ composite_type: { $exists: true } })})"
        command = f"bash -c \"mongosh -u {mongodb_username} -p {mongodb_password} --eval 'use das' --eval '{mongodb_command}' | tail -n 1\""

        result = self._exec_container(command)

        return json.loads(result.output)

    def get_count_atoms(self) -> int:
        collection_stats = self.get_collection_stats()
        count_atoms = int(collection_stats.get("atoms", 0))

        return count_atoms
