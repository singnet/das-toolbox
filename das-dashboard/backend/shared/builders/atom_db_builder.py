from shared.builders.builder_helpers import _get, _is_missing, _require
from shared.utils.adapter_context_mapping import validate_context_mapping_path


class AtomDbBuilder:

    REDIS_IMAGE = "redis:7.2.3-alpine"
    MONGO_IMAGE = "mongodb/mongodb-community-server:8.2-ubuntu2204"
    MORK_IMAGE = "trueagi/das:mork-server-1.0.4"

    _REDIS_MONGO_FIELDS = (
        "redis_endpoint",
        "redis_port",
        "mongo_endpoint",
        "mongo_port",
        "mongo_username",
        "mongo_password",
    )

    _MORK_CONNECTION_FIELDS = (
        "mork_endpoint",
        "mork_port",
    )

    _MONGO_CONNECTION_FIELDS = (
        "mongo_endpoint",
        "mongo_port",
        "mongo_username",
        "mongo_password",
    )

    _ADAPTER_FIELDS = (
        "adapter_endpoint",
        "adapter_port",
        "adapter_type",
        "db_host",
        "db_port",
        "db_name",
        "db_username",
        "db_password",
        "context_mapping_path",
        "export_metta_enabled",
        "export_metta_output_dir",
        "persistence_reuse_mongodb",
        "atomdb_backend",
    )

    def __init__(self, profile_username: str = ""):
        self.profile_username = profile_username or ""

    def build(self, flat_atomdb: dict) -> dict:
        _require(flat_atomdb, "atomdb_type")

        atomdb_type = flat_atomdb["atomdb_type"]
        builders = {
            "redismongodb": self._build_redis_mongo,
            "morkdb": self._build_mork_mongo,
            "inmemorydb": self._build_inmemory_db,
            "remotedb": self._build_remote_db,
            "adapterdb": self._build_adapter_db,
        }

        builder = builders.get(atomdb_type)
        if not builder:
            raise ValueError(f"Unsupported atomdb type: {atomdb_type}")

        return builder(flat_atomdb)

    @staticmethod
    def _endpoint(host: str, port) -> str:
        return f"{host}:{port}"

    @classmethod
    def _resolve_node_username(cls, username: str) -> str:
        if not username or username in ("root", "default"):
            return ""
        return username

    @classmethod
    def apply_profile_usernames(cls, nested_config: dict, profile_username: str) -> dict:
        if not isinstance(nested_config, dict):
            return nested_config

        atomdb = nested_config.get("atomdb")
        if isinstance(atomdb, dict):
            cls._fill_empty_node_usernames(atomdb, profile_username)

        return nested_config

    @classmethod
    def _fill_empty_node_usernames(cls, atomdb: dict, profile_username: str) -> None:
        atomdb_type = atomdb.get("type")

        if atomdb_type == "redismongodb":
            cls._fill_nodes_username(atomdb.get("redis"), profile_username)
            cls._fill_nodes_username(atomdb.get("mongodb"), profile_username)
        elif atomdb_type == "morkdb":
            cls._fill_nodes_username(atomdb.get("mongodb"), profile_username)
        elif atomdb_type == "adapterdb":
            adapter = atomdb.get("adapterdb")
            if isinstance(adapter, dict):
                backend = adapter.get("atomdb_backend")
                if isinstance(backend, dict):
                    cls._fill_empty_node_usernames(backend, profile_username)

    @classmethod
    def _fill_nodes_username(cls, database_section: dict, profile_username: str) -> None:
        if not isinstance(database_section, dict):
            return

        for node in database_section.get("nodes") or []:
            if not isinstance(node, dict):
                continue
            if not cls._resolve_node_username(node.get("username", "")):
                node["username"] = profile_username or ""

    def _build_nodes(
        self,
        flat_nodes: list | None,
        *,
        endpoint_host: str,
        cluster_enabled: bool,
        field_name: str,
    ) -> list[dict]:
        if cluster_enabled and not isinstance(flat_nodes, list):
            raise ValueError(f"{field_name} must be a list when cluster mode is enabled")

        nodes = []
        for entry in flat_nodes or []:
            if not isinstance(entry, dict):
                continue
            nodes.append({
                "context": entry.get("context", "default"),
                "ip": entry.get("ip", ""),
                "username": self._resolve_node_username(entry.get("username", "")) or self.profile_username,
            })

        if nodes:
            return nodes

        if cluster_enabled:
            raise ValueError(f"{field_name} cannot be empty when cluster mode is enabled")

        return [{
            "context": "default",
            "ip": endpoint_host or "localhost",
            "username": self.profile_username,
        }]

    def _build_redis_mongo(self, flat: dict, *, where: str = "atomdb") -> dict:
        _require(flat, *self._REDIS_MONGO_FIELDS, label=where)

        redis_host = flat["redis_endpoint"]
        redis_port = flat["redis_port"]
        mongo_host = flat["mongo_endpoint"]
        mongo_port = flat["mongo_port"]
        redis_cluster = flat.get("redis_cluster", False)
        mongo_cluster = flat.get("mongo_cluster", False)

        return {
            "type": "redismongodb",
            "redis": {
                "image": self.REDIS_IMAGE,
                "endpoint": self._endpoint(redis_host, redis_port),
                "cluster": redis_cluster,
                "nodes": self._build_nodes(
                    flat.get("redis_nodes"),
                    endpoint_host=redis_host,
                    cluster_enabled=redis_cluster,
                    field_name=f"{where}.redis_nodes",
                ),
            },
            "mongodb": {
                "image": self.MONGO_IMAGE,
                "endpoint": self._endpoint(mongo_host, mongo_port),
                "username": flat["mongo_username"],
                "password": flat["mongo_password"],
                "cluster": mongo_cluster,
                "cluster_secret_key": None,
                "nodes": self._build_nodes(
                    flat.get("mongo_nodes"),
                    endpoint_host=mongo_host,
                    cluster_enabled=mongo_cluster,
                    field_name=f"{where}.mongo_nodes",
                ),
            },
        }

    def _build_mork_mongo(self, flat: dict, *, where: str = "atomdb") -> dict:
        _require(flat, *self._MORK_CONNECTION_FIELDS, *self._MONGO_CONNECTION_FIELDS, label=where)

        mongo_host = flat["mongo_endpoint"]
        mongo_port = flat["mongo_port"]
        mongo_cluster = flat.get("mongo_cluster", False)

        return {
            "type": "morkdb",
            "mongodb": {
                "image": self.MONGO_IMAGE,
                "endpoint": self._endpoint(mongo_host, mongo_port),
                "username": flat["mongo_username"],
                "password": flat["mongo_password"],
                "cluster": mongo_cluster,
                "cluster_secret_key": None,
                "nodes": self._build_nodes(
                    flat.get("mongo_nodes"),
                    endpoint_host=mongo_host,
                    cluster_enabled=mongo_cluster,
                    field_name=f"{where}.mongo_nodes",
                ),
            },
            "morkdb": {
                "image": self.MORK_IMAGE,
                "endpoint": self._endpoint(flat["mork_endpoint"], flat["mork_port"]),
            },
        }

    def _build_inmemory_db(self, _flat: dict, *, where: str = "atomdb") -> dict:
        return {"type": "inmemorydb"}

    def _build_remote_db(self, flat: dict) -> dict:
        _require(flat, "remote_peers", label="atomdb")

        remote_peers = flat["remote_peers"]
        if not isinstance(remote_peers, list):
            raise ValueError("atomdb.remote_peers must be a list")

        peers = []

        for index, peer in enumerate(remote_peers):
            peer_where = f"atomdb.remote_peers[{index}]"
            _require(peer, "uid", "type", "context", "local_persistence", label=peer_where)

            peer_type = peer["type"]
            peer_config = {
                "uid": peer["uid"],
                "type": peer_type,
                "context": peer["context"],
            }

            if peer_type == "redismongodb":
                _require(peer, *self._REDIS_MONGO_FIELDS, label=peer_where)
                peer_config["redis"] = {
                    "endpoint": self._endpoint(peer["redis_endpoint"], peer["redis_port"]),
                    "cluster": False,
                }
                peer_config["mongodb"] = {
                    "endpoint": self._endpoint(peer["mongo_endpoint"], peer["mongo_port"]),
                    "username": peer["mongo_username"],
                    "password": peer["mongo_password"],
                }

            elif peer_type == "morkdb":
                _require(peer, *self._MORK_CONNECTION_FIELDS, *self._MONGO_CONNECTION_FIELDS, label=peer_where)
                peer_config["morkdb"] = {
                    "endpoint": self._endpoint(peer["mork_endpoint"], peer["mork_port"]),
                }
                peer_config["mongodb"] = {
                    "endpoint": self._endpoint(peer["mongo_endpoint"], peer["mongo_port"]),
                    "username": peer["mongo_username"],
                    "password": peer["mongo_password"],
                }

            else:
                raise ValueError(f"Unsupported remote peer type at {peer_where}: {peer_type}")

            peer_config["local_persistence"] = self._build_local_persistence(
                peer["local_persistence"],
                where=f"{peer_where}.local_persistence",
            )

            peers.append(peer_config)

        return {
            "type": "remotedb",
            "remote_peers": peers,
        }

    def _build_local_persistence(self, flat: dict, *, where: str) -> dict:
        _require(flat, "type", label=where)

        lp_type = flat["type"]
        result = {"type": lp_type}

        if lp_type == "inmemorydb":
            if not _is_missing(flat, "context"):
                result["context"] = flat["context"]
            return result

        if lp_type == "redismongodb":
            _require(flat, "context", *self._REDIS_MONGO_FIELDS, label=where)
            result["context"] = flat["context"]
            result["redis"] = {
                "endpoint": self._endpoint(flat["redis_endpoint"], flat["redis_port"]),
                "cluster": False,
            }
            result["mongodb"] = {
                "endpoint": self._endpoint(flat["mongo_endpoint"], flat["mongo_port"]),
                "username": flat["mongo_username"],
                "password": flat["mongo_password"],
            }
            return result

        if lp_type == "morkdb":
            _require(flat, "context", *self._MORK_CONNECTION_FIELDS, *self._MONGO_CONNECTION_FIELDS, label=where)
            result["context"] = flat["context"]
            result["morkdb"] = {
                "endpoint": self._endpoint(flat["mork_endpoint"], flat["mork_port"]),
            }
            result["mongodb"] = {
                "endpoint": self._endpoint(flat["mongo_endpoint"], flat["mongo_port"]),
                "username": flat["mongo_username"],
                "password": flat["mongo_password"],
            }
            return result

        raise ValueError(f"Unsupported local_persistence type at {where}: {lp_type}")

    def _build_backend_section(self, flat_backend: dict) -> dict:
        _require(flat_backend, "type", label="atomdb.atomdb_backend")

        backend_type = flat_backend["type"]
        builders = {
            "redismongodb": self._build_redis_mongo,
            "morkdb": self._build_mork_mongo,
            "inmemorydb": self._build_inmemory_db,
        }

        builder = builders.get(backend_type)
        if not builder:
            raise ValueError(f"Unsupported atomdb_backend type: {backend_type}")

        return builder(flat_backend, where="atomdb.atomdb_backend")

    def _build_adapter_db(self, flat: dict) -> dict:
        _require(flat, *self._ADAPTER_FIELDS, label="atomdb")

        context_mapping_path = validate_context_mapping_path(flat["context_mapping_path"])

        return {
            "type": "adapterdb",
            "adapterdb": {
                "endpoint": self._endpoint(flat["adapter_endpoint"], flat["adapter_port"]),
                "type": flat["adapter_type"],
                "database_credentials": {
                    "host": flat["db_host"],
                    "port": flat["db_port"],
                    "username": flat["db_username"],
                    "password": flat["db_password"],
                    "database": flat["db_name"],
                },
                "context_mapping_paths": [context_mapping_path],
                "export_metta_on_mapping": {
                    "enabled": flat["export_metta_enabled"],
                    "output_dir": flat.get("export_metta_output_dir", ""),
                },
                "persistence": {
                    "reuse_mongodb": flat["persistence_reuse_mongodb"],
                },
                "atomdb_backend": self._build_backend_section(flat["atomdb_backend"]),
            },
        }
