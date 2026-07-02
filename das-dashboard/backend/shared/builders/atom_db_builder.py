from shared.builders.builder_helpers import _get, _is_missing, _require
from shared.utils.adapter_context_mapping import validate_context_mapping_path

class AtomDbBuilder:

    REDIS_IMAGE = "redis:7.2.3-alpine"
    MONGO_IMAGE = "mongodb/mongodb-community-server:8.2-ubuntu2204"
    MORK_IMAGE = "trueagi/das:mork-server-1.0.4"

    def __init__(self, profile_username: str = ""):
        self.profile_username = profile_username or ""

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

    def build(self, atomdb) -> dict:
        _require(atomdb, "atomdb_type")

        handlers = {
            "redismongodb": self._build_redis_mongo,
            "morkdb": self._build_mork_mongo,
            "inmemorydb": self._build_inmemory_db,
            "remotedb": self._build_remote_db,
            "adapterdb": self._build_adapter_db,
        }

        atomdb_type = _get(atomdb, "atomdb_type")
        builder = handlers.get(atomdb_type)

        if not builder:
            raise ValueError(f"Unsupported atomdb type: {atomdb_type}")

        return builder(atomdb)

    @staticmethod
    def _endpoint(host, port) -> str:
        return f"{host}:{port}"

    @classmethod
    def _validate_cluster_nodes(cls, source, cluster_key: str, nodes_key: str, label: str) -> None:
        if not _get(source, cluster_key, False):
            return

        _require(source, nodes_key, label=label)
        nodes = _get(source, nodes_key)

        if not isinstance(nodes, list):
            raise ValueError(f"{label}.{nodes_key} must be a list when {cluster_key} is true")

    @classmethod
    def _resolve_node_username(cls, context, username, profile_username: str) -> str:
        if not username or username in ("root", "default"):
            return profile_username or ""
        return username

    @classmethod
    def _patch_section_nodes(cls, section, profile_username: str) -> None:
        if not isinstance(section, dict):
            return

        nodes = section.get("nodes")
        if not isinstance(nodes, list):
            return

        for node in nodes:
            if not isinstance(node, dict):
                continue
            node["username"] = cls._resolve_node_username(
                node.get("context", "default"),
                node.get("username", ""),
                profile_username,
            )

    @classmethod
    def apply_profile_usernames(cls, nested_config: dict, profile_username: str) -> dict:
        if not isinstance(nested_config, dict):
            return nested_config

        atomdb = nested_config.get("atomdb")
        if isinstance(atomdb, dict):
            cls._patch_atomdb_nodes(atomdb, profile_username)

        return nested_config

    @classmethod
    def _patch_atomdb_nodes(cls, atomdb: dict, profile_username: str) -> None:
        atomdb_type = atomdb.get("type")

        if atomdb_type == "redismongodb":
            cls._patch_section_nodes(atomdb.get("redis"), profile_username)
            cls._patch_section_nodes(atomdb.get("mongodb"), profile_username)
        elif atomdb_type == "morkdb":
            cls._patch_section_nodes(atomdb.get("mongodb"), profile_username)
        elif atomdb_type == "adapterdb":
            adapter = atomdb.get("adapterdb")
            if isinstance(adapter, dict):
                backend = adapter.get("atomdb_backend")
                if isinstance(backend, dict):
                    cls._patch_atomdb_nodes(backend, profile_username)

    def _map_cluster_nodes(self, nodes) -> list:
        if not isinstance(nodes, list):
            return []

        return [
            {
                "context": _get(node, "context", "default"),
                "ip": _get(node, "ip", ""),
                "username": self._resolve_node_username(
                    _get(node, "context", "default"),
                    _get(node, "username", ""),
                    self.profile_username,
                ),
            }
            for node in nodes
        ]

    def _with_nodes(self, section: dict, source, cluster_key: str, nodes_key: str, label: str) -> dict:
        cluster = _get(source, cluster_key, False)
        raw_nodes = _get(source, nodes_key, [])

        if cluster:
            self._validate_cluster_nodes(source, cluster_key, nodes_key, label)
            section["nodes"] = self._map_cluster_nodes(raw_nodes)
        elif raw_nodes:
            section["nodes"] = self._map_cluster_nodes(raw_nodes)

        return section

    def _build_redis_mongo(self, source, *, label: str = "atomdb") -> dict:
        _require(source, *self._REDIS_MONGO_FIELDS, label=label)
        self._validate_cluster_nodes(source, "redis_cluster", "redis_nodes", label)
        self._validate_cluster_nodes(source, "mongo_cluster", "mongo_nodes", label)

        redis = {
            "image": self.REDIS_IMAGE,
            "endpoint": self._endpoint(
                _get(source, "redis_endpoint"),
                _get(source, "redis_port"),
            ),
            "cluster": _get(source, "redis_cluster", False),
        }
        self._with_nodes(redis, source, "redis_cluster", "redis_nodes", label)

        mongodb = {
            "image": self.MONGO_IMAGE,
            "endpoint": self._endpoint(
                _get(source, "mongo_endpoint"),
                _get(source, "mongo_port"),
            ),
            "username": _get(source, "mongo_username"),
            "password": _get(source, "mongo_password"),
            "cluster": _get(source, "mongo_cluster", False),
            "cluster_secret_key": None,
        }
        self._with_nodes(mongodb, source, "mongo_cluster", "mongo_nodes", label)

        return {
            "type": "redismongodb",
            "redis": redis,
            "mongodb": mongodb,
        }

    def _build_mork_mongo(self, source, *, label: str = "atomdb") -> dict:
        _require(source, *self._MORK_CONNECTION_FIELDS, *self._MONGO_CONNECTION_FIELDS, label=label)
        self._validate_cluster_nodes(source, "mongo_cluster", "mongo_nodes", label)

        mongodb = {
            "image": self.MONGO_IMAGE,
            "endpoint": self._endpoint(
                _get(source, "mongo_endpoint"),
                _get(source, "mongo_port"),
            ),
            "username": _get(source, "mongo_username"),
            "password": _get(source, "mongo_password"),
            "cluster": _get(source, "mongo_cluster", False),
            "cluster_secret_key": None,
        }
        self._with_nodes(mongodb, source, "mongo_cluster", "mongo_nodes", label)

        return {
            "type": "morkdb",
            "mongodb": mongodb,
            "morkdb": {
                "image": self.MORK_IMAGE,
                "endpoint": self._endpoint(
                    _get(source, "mork_endpoint"),
                    _get(source, "mork_port"),
                ),
            },
        }

    def _build_inmemory_db(self, _source, *, label: str = "atomdb") -> dict:
        return {"type": "inmemorydb"}

    def _build_remote_db(self, atomdb) -> dict:
        _require(atomdb, "remote_peers", label="atomdb")

        remote_peers = _get(atomdb, "remote_peers")
        if not isinstance(remote_peers, list):
            raise ValueError("atomdb.remote_peers must be a list")

        peers = []

        for index, peer in enumerate(remote_peers):
            peer_label = f"atomdb.remote_peers[{index}]"
            _require(peer, "uid", "type", "context", "local_persistence", label=peer_label)

            peer_type = _get(peer, "type")
            peer_config = {
                "uid": _get(peer, "uid"),
                "type": peer_type,
                "context": _get(peer, "context"),
            }

            if peer_type == "redismongodb":
                _require(peer, *self._REDIS_MONGO_FIELDS, label=peer_label)
                peer_config["redis"] = {
                    "endpoint": self._endpoint(
                        _get(peer, "redis_endpoint"),
                        _get(peer, "redis_port"),
                    ),
                    "cluster": False,
                }
                peer_config["mongodb"] = {
                    "endpoint": self._endpoint(
                        _get(peer, "mongo_endpoint"),
                        _get(peer, "mongo_port"),
                    ),
                    "username": _get(peer, "mongo_username"),
                    "password": _get(peer, "mongo_password"),
                }

            elif peer_type == "morkdb":
                _require(peer, *self._MORK_CONNECTION_FIELDS, *self._MONGO_CONNECTION_FIELDS, label=peer_label)
                peer_config["morkdb"] = {
                    "endpoint": self._endpoint(
                        _get(peer, "mork_endpoint"),
                        _get(peer, "mork_port"),
                    ),
                }
                peer_config["mongodb"] = {
                    "endpoint": self._endpoint(
                        _get(peer, "mongo_endpoint"),
                        _get(peer, "mongo_port"),
                    ),
                    "username": _get(peer, "mongo_username"),
                    "password": _get(peer, "mongo_password"),
                }

            else:
                raise ValueError(f"Unsupported remote peer type at {peer_label}: {peer_type}")

            peer_config["local_persistence"] = self._build_local_persistence(
                _get(peer, "local_persistence"),
                label=f"{peer_label}.local_persistence",
            )

            peers.append(peer_config)

        return {
            "type": "remotedb",
            "remote_peers": peers,
        }

    def _build_local_persistence(self, local, *, label: str) -> dict:
        _require(local, "type", label=label)

        lp_type = _get(local, "type")
        result = {"type": lp_type}

        if lp_type == "inmemorydb":
            if not _is_missing(local, "context"):
                result["context"] = _get(local, "context")
            return result

        if lp_type == "redismongodb":
            _require(local, "context", *self._REDIS_MONGO_FIELDS, label=label)
            result["context"] = _get(local, "context")
            result["redis"] = {
                "endpoint": self._endpoint(
                    _get(local, "redis_endpoint"),
                    _get(local, "redis_port"),
                ),
                "cluster": False,
            }
            result["mongodb"] = {
                "endpoint": self._endpoint(
                    _get(local, "mongo_endpoint"),
                    _get(local, "mongo_port"),
                ),
                "username": _get(local, "mongo_username"),
                "password": _get(local, "mongo_password"),
            }
            return result

        if lp_type == "morkdb":
            _require(local, "context", *self._MORK_CONNECTION_FIELDS, *self._MONGO_CONNECTION_FIELDS, label=label)
            result["context"] = _get(local, "context")
            result["morkdb"] = {
                "endpoint": self._endpoint(
                    _get(local, "mork_endpoint"),
                    _get(local, "mork_port"),
                ),
            }
            result["mongodb"] = {
                "endpoint": self._endpoint(
                    _get(local, "mongo_endpoint"),
                    _get(local, "mongo_port"),
                ),
                "username": _get(local, "mongo_username"),
                "password": _get(local, "mongo_password"),
            }
            return result

        raise ValueError(f"Unsupported local_persistence type at {label}: {lp_type}")

    def _build_backend_section(self, backend) -> dict:
        _require(backend, "type", label="atomdb.atomdb_backend")

        backend_type = _get(backend, "type")
        handlers = {
            "redismongodb": self._build_redis_mongo,
            "morkdb": self._build_mork_mongo,
            "inmemorydb": self._build_inmemory_db,
        }

        handler = handlers.get(backend_type)
        if not handler:
            raise ValueError(f"Unsupported atomdb_backend type: {backend_type}")

        return handler(backend, label="atomdb.atomdb_backend")

    def _build_adapter_db(self, atomdb) -> dict:
        _require(atomdb, *self._ADAPTER_FIELDS, label="atomdb")

        context_mapping_path = validate_context_mapping_path(
            _get(atomdb, "context_mapping_path")
        )
        export_metta_output_dir = _get(atomdb, "export_metta_output_dir", "")

        return {
            "type": "adapterdb",
            "adapterdb": {
                "endpoint": self._endpoint(
                    _get(atomdb, "adapter_endpoint"),
                    _get(atomdb, "adapter_port"),
                ),
                "type": _get(atomdb, "adapter_type"),
                "database_credentials": {
                    "host": _get(atomdb, "db_host"),
                    "port": _get(atomdb, "db_port"),
                    "username": _get(atomdb, "db_username"),
                    "password": _get(atomdb, "db_password"),
                    "database": _get(atomdb, "db_name"),
                },
                "context_mapping_paths": [context_mapping_path],
                "export_metta_on_mapping": {
                    "enabled": _get(atomdb, "export_metta_enabled"),
                    "output_dir": export_metta_output_dir,
                },
                "persistence": {
                    "reuse_mongodb": _get(atomdb, "persistence_reuse_mongodb")
                },
                "atomdb_backend": self._build_backend_section(
                    _get(atomdb, "atomdb_backend")
                ),
            },
        }
