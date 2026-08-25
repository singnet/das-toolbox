from shared.utils.path_utils import split_endpoint

DEFAULT_ENDPOINT_HOST = "0.0.0.0"


class NestedConfigMapper:

    @staticmethod
    def to_flat(nested: dict) -> dict:
        flat: dict = {}

        atomdb = nested.get("atomdb")
        if atomdb:
            flat["atomdb"] = NestedConfigMapper._atomdb_to_flat(atomdb)

        agents = nested.get("agents")
        if agents:
            flat.update(NestedConfigMapper._agents_to_flat(agents))

        environment = nested.get("environment")
        if environment:
            flat["environment"] = NestedConfigMapper._environment_to_flat(environment)

        return flat

    @staticmethod
    def _environment_to_flat(environment: dict) -> dict:
        jupyter = environment.get("jupyter", {})
        return {"jupyter_endpoint": jupyter.get("endpoint", f"{DEFAULT_ENDPOINT_HOST}:40019")}

    @staticmethod
    def _agents_to_flat(agents: dict) -> dict:
        flat: dict = {}

        if "attention" in agents:
            flat["agents.attention"] = {"endpoint": agents["attention"].get("endpoint")}

        if "base_query" in agents:
            flat["agents.base_query"] = dict(agents["base_query"].get("params", {}))

        agent_keys_with_ports = (
            "query",
            "link_creation",
            "inference",
            "evolution",
            "context",
            "atomdb",
            "command_router",
        )

        for agent_key in agent_keys_with_ports:
            section = agents.get(agent_key)
            if not section:
                continue

            entry = {
                "endpoint": section.get("endpoint"),
                "ports_range": section.get("ports_range"),
            }

            params = section.get("params")
            if params:
                entry.update(params)

            flat[f"agents.{agent_key}"] = entry

            if agent_key == "command_router":
                http_api = section.get("http_api") or {}
                _, http_port = split_endpoint(
                    http_api.get("endpoint"),
                    DEFAULT_ENDPOINT_HOST,
                    40009,
                )
                entry["http_api_port"] = http_port

        return flat

    @staticmethod
    def _atomdb_to_flat(atomdb: dict) -> dict:
        atomdb_type = atomdb.get("type")

        if atomdb_type == "redismongodb":
            return NestedConfigMapper._redis_mongo_to_flat(atomdb)

        if atomdb_type == "morkdb":
            return NestedConfigMapper._mork_mongo_to_flat(atomdb)

        if atomdb_type == "inmemorydb":
            return {"atomdb_type": "inmemorydb"}

        if atomdb_type == "remotedb":
            return NestedConfigMapper._remote_db_to_flat(atomdb)

        if atomdb_type == "adapterdb":
            return NestedConfigMapper._adapter_db_to_flat(atomdb)

        raise ValueError(f"Unsupported atomdb type in nested config: {atomdb_type}")

    @staticmethod
    def _redis_mongo_section_to_flat(source: dict, *, prefix: str = "") -> dict:
        redis = source.get("redis", {})
        mongo = source.get("mongodb", {})

        redis_host, redis_port = split_endpoint(redis.get("endpoint"), DEFAULT_ENDPOINT_HOST, 40020)
        mongo_host, mongo_port = split_endpoint(mongo.get("endpoint"), DEFAULT_ENDPOINT_HOST, 40021)

        result = {
            f"{prefix}redis_endpoint": redis_host,
            f"{prefix}redis_port": redis_port,
            f"{prefix}mongo_endpoint": mongo_host,
            f"{prefix}mongo_port": mongo_port,
            f"{prefix}mongo_username": mongo.get("username", "admin"),
            f"{prefix}mongo_password": mongo.get("password", "admin"),
            f"{prefix}redis_cluster": redis.get("cluster", False),
            f"{prefix}mongo_cluster": mongo.get("cluster", False),
            f"{prefix}redis_nodes": redis.get("nodes", []),
            f"{prefix}mongo_nodes": mongo.get("nodes", []),
        }

        if prefix:
            return {key.removeprefix(prefix): value for key, value in result.items()}

        return result

    @staticmethod
    def _redis_mongo_to_flat(atomdb: dict) -> dict:
        flat = NestedConfigMapper._redis_mongo_section_to_flat(atomdb)
        flat["atomdb_type"] = "redismongodb"
        return flat

    @staticmethod
    def _mork_mongo_to_flat(atomdb: dict) -> dict:
        mongo = atomdb.get("mongodb", {})
        mork = atomdb.get("morkdb", {})

        mongo_host, mongo_port = split_endpoint(mongo.get("endpoint"), DEFAULT_ENDPOINT_HOST, 40021)
        mork_host, mork_port = split_endpoint(mork.get("endpoint"), DEFAULT_ENDPOINT_HOST, 40022)

        return {
            "atomdb_type": "morkdb",
            "mork_endpoint": mork_host,
            "mork_port": mork_port,
            "mongo_endpoint": mongo_host,
            "mongo_port": mongo_port,
            "mongo_username": mongo.get("username", "admin"),
            "mongo_password": mongo.get("password", "admin"),
            "mongo_cluster": mongo.get("cluster", False),
            "mongo_nodes": mongo.get("nodes", []),
        }

    @staticmethod
    def _backend_to_flat(backend: dict) -> dict:
        backend_type = backend.get("type", "inmemorydb")

        if backend_type == "inmemorydb":
            return {"type": "inmemorydb"}

        if backend_type == "redismongodb":
            return {"type": "redismongodb", **NestedConfigMapper._redis_mongo_section_to_flat(backend)}

        if backend_type == "morkdb":
            mongo = backend.get("mongodb", {})
            mork = backend.get("morkdb", {})
            mongo_host, mongo_port = split_endpoint(mongo.get("endpoint"), DEFAULT_ENDPOINT_HOST, 40021)
            mork_host, mork_port = split_endpoint(mork.get("endpoint"), DEFAULT_ENDPOINT_HOST, 40022)

            return {
                "type": "morkdb",
                "mork_endpoint": mork_host,
                "mork_port": mork_port,
                "mongo_endpoint": mongo_host,
                "mongo_port": mongo_port,
                "mongo_username": mongo.get("username", "admin"),
                "mongo_password": mongo.get("password", "admin"),
                "mongo_cluster": mongo.get("cluster", False),
                "mongo_nodes": mongo.get("nodes", []),
            }

        return {"type": backend_type}

    @staticmethod
    def _adapter_db_to_flat(atomdb: dict) -> dict:
        adapterdb = atomdb.get("adapterdb", {})
        credentials = adapterdb.get("database_credentials", {})
        metta = adapterdb.get("export_metta_on_mapping", {})
        mapping_paths = adapterdb.get("context_mapping_paths") or []

        adapter_host, adapter_port = split_endpoint(adapterdb.get("endpoint"), DEFAULT_ENDPOINT_HOST, 40023)

        return {
            "atomdb_type": "adapterdb",
            "adapter_type": adapterdb.get("type", "postgres"),
            "adapter_endpoint": adapter_host,
            "adapter_port": adapter_port,
            "db_host": credentials.get("host", ""),
            "db_port": credentials.get("port", 5432),
            "db_name": credentials.get("database", ""),
            "db_username": credentials.get("username", ""),
            "db_password": credentials.get("password", ""),
            "context_mapping_path": mapping_paths[0] if mapping_paths else "",
            "export_metta_enabled": metta.get("enabled", True),
            "export_metta_output_dir": metta.get("output_dir", ""),
            "persistence_reuse_mongodb": adapterdb.get("persistence", {}).get("reuse_mongodb", True),
            "atomdb_backend": NestedConfigMapper._backend_to_flat(adapterdb.get("atomdb_backend", {})),
        }

    @staticmethod
    def _local_persistence_to_flat(local: dict) -> dict:
        lp_type = local.get("type", "inmemorydb")
        result = {"type": lp_type}

        if lp_type == "inmemorydb":
            if local.get("context"):
                result["context"] = local["context"]
            return result

        if lp_type == "redismongodb":
            redis = local.get("redis", {})
            mongo = local.get("mongodb", {})
            redis_host, redis_port = split_endpoint(redis.get("endpoint"), DEFAULT_ENDPOINT_HOST, 40020)
            mongo_host, mongo_port = split_endpoint(mongo.get("endpoint"), DEFAULT_ENDPOINT_HOST, 40021)

            result.update({
                "context": local.get("context", ""),
                "redis_endpoint": redis_host,
                "redis_port": redis_port,
                "mongo_endpoint": mongo_host,
                "mongo_port": mongo_port,
                "mongo_username": mongo.get("username", "admin"),
                "mongo_password": mongo.get("password", "admin"),
            })
            return result

        if lp_type == "morkdb":
            mongo = local.get("mongodb", {})
            mork = local.get("morkdb", {})
            mongo_host, mongo_port = split_endpoint(mongo.get("endpoint"), DEFAULT_ENDPOINT_HOST, 40021)
            mork_host, mork_port = split_endpoint(mork.get("endpoint"), DEFAULT_ENDPOINT_HOST, 40022)

            result.update({
                "context": local.get("context", ""),
                "mork_endpoint": mork_host,
                "mork_port": mork_port,
                "mongo_endpoint": mongo_host,
                "mongo_port": mongo_port,
                "mongo_username": mongo.get("username", "admin"),
                "mongo_password": mongo.get("password", "admin"),
            })

        return result

    @staticmethod
    def _remote_db_to_flat(atomdb: dict) -> dict:
        peers = []

        for peer in atomdb.get("remote_peers", []):
            peer_type = peer.get("type")
            flat_peer = {
                "uid": peer.get("uid"),
                "type": peer_type,
                "context": peer.get("context"),
                "local_persistence": NestedConfigMapper._local_persistence_to_flat(
                    peer.get("local_persistence", {})
                ),
            }

            if peer_type == "redismongodb":
                redis = peer.get("redis", {})
                mongo = peer.get("mongodb", {})
                redis_host, redis_port = split_endpoint(redis.get("endpoint"), DEFAULT_ENDPOINT_HOST, 40020)
                mongo_host, mongo_port = split_endpoint(mongo.get("endpoint"), DEFAULT_ENDPOINT_HOST, 40021)
                flat_peer.update({
                    "redis_endpoint": redis_host,
                    "redis_port": redis_port,
                    "mongo_endpoint": mongo_host,
                    "mongo_port": mongo_port,
                    "mongo_username": mongo.get("username", "admin"),
                    "mongo_password": mongo.get("password", "admin"),
                })

            elif peer_type == "morkdb":
                mongo = peer.get("mongodb", {})
                mork = peer.get("morkdb", {})
                mongo_host, mongo_port = split_endpoint(mongo.get("endpoint"), DEFAULT_ENDPOINT_HOST, 40021)
                mork_host, mork_port = split_endpoint(mork.get("endpoint"), DEFAULT_ENDPOINT_HOST, 40022)
                flat_peer.update({
                    "mork_endpoint": mork_host,
                    "mork_port": mork_port,
                    "mongo_endpoint": mongo_host,
                    "mongo_port": mongo_port,
                    "mongo_username": mongo.get("username", "admin"),
                    "mongo_password": mongo.get("password", "admin"),
                })

            peers.append(flat_peer)

        return {"atomdb_type": "remotedb", "remote_peers": peers}
