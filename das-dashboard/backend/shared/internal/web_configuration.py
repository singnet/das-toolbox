import json
import os

from shared.internal.constants import (
    CONFIG_PATH,
    DEFAULT_WEBPROFILE_PATH as PROFILE_PATH,
    LOCAL_HOSTS,
)

# Agent section keys mapped to das-cli service command names.
AGENT_SERVICE_COMMANDS = {
    "attention": "attention-broker",
    "query": "query-agent",
    "link_creation": "link-creation-agent",
    "inference": "inference-agent",
    "evolution": "evolution-agent",
    "context": "context-broker",
    "atomdb": "atomdb-broker",
    "command_router": "command-router-agent",
}


class WebConfiguration:

    _instance = None
    config_dictionary: dict[str, dict] = {}
    user_profile: dict[str, str] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load_user_profile(self):
        if not os.path.exists(PROFILE_PATH):
            self.user_profile = {}
            return

        try:
            with open(PROFILE_PATH, "r") as f:
                self.user_profile = json.load(f)
        except:
            self.user_profile = {}

    def load_config_dictionary(self):
        if not os.path.exists(CONFIG_PATH):
            self.config_dictionary = {}
            return

        try:
            with open(CONFIG_PATH, "r") as f:
                config = json.load(f)

            if isinstance(config, list):
                config = config[0]

            self.config_dictionary = self.map_services(config)
        except:
            self.config_dictionary = {}

    @staticmethod
    def _register_endpoint(services: dict, name: str, endpoint: str | None) -> None:
        if not endpoint or not isinstance(endpoint, str):
            return

        host, _, port = endpoint.partition(":")
        if not host:
            return

        try:
            port_num = int(port) if port else 0
        except ValueError:
            port_num = 0

        services[name] = {
            "host": host,
            "port": port_num,
        }

    @classmethod
    def _map_redis_mongo(cls, services: dict, section: dict, *, db_name: str = "db") -> None:
        redis = section.get("redis") or {}
        mongo = section.get("mongodb") or {}

        cls._register_endpoint(services, db_name, mongo.get("endpoint"))
        cls._register_endpoint(services, "redis", redis.get("endpoint"))

    @classmethod
    def _map_mork_mongo(cls, services: dict, section: dict, *, db_name: str = "db") -> None:
        mongo = section.get("mongodb") or {}
        mork = section.get("morkdb") or {}

        cls._register_endpoint(services, db_name, mongo.get("endpoint"))
        cls._register_endpoint(services, "morkdb", mork.get("endpoint"))

    @classmethod
    def _map_remote_peer(cls, services: dict, peer: dict, index: int) -> None:
        uid = peer.get("uid") or f"peer-{index}"
        prefix = f"remote-{uid}"
        peer_type = peer.get("type")

        if peer_type == "redismongodb":
            cls._register_endpoint(
                services,
                f"{prefix}-redis",
                (peer.get("redis") or {}).get("endpoint"),
            )
            cls._register_endpoint(
                services,
                f"{prefix}-mongodb",
                (peer.get("mongodb") or {}).get("endpoint"),
            )
        elif peer_type == "morkdb":
            cls._register_endpoint(
                services,
                f"{prefix}-morkdb",
                (peer.get("morkdb") or {}).get("endpoint"),
            )
            cls._register_endpoint(
                services,
                f"{prefix}-mongodb",
                (peer.get("mongodb") or {}).get("endpoint"),
            )

        local_persistence = peer.get("local_persistence") or {}
        cls._map_atomdb_section(
            services,
            local_persistence,
            db_name=f"{prefix}-local-db",
        )

    @classmethod
    def _map_atomdb_section(cls, services: dict, atomdb: dict, *, db_name: str = "db") -> None:
        if not isinstance(atomdb, dict):
            return

        atomdb_type = atomdb.get("type")

        if atomdb_type == "redismongodb":
            cls._map_redis_mongo(services, atomdb, db_name=db_name)
            return

        if atomdb_type == "morkdb":
            cls._map_mork_mongo(services, atomdb, db_name=db_name)
            return

        if atomdb_type == "adapterdb":
            adapterdb = atomdb.get("adapterdb") or {}
            cls._register_endpoint(services, "adapterdb", adapterdb.get("endpoint"))
            cls._map_atomdb_section(
                services,
                adapterdb.get("atomdb_backend") or {},
                db_name="adapter-backend",
            )
            return

        if atomdb_type == "remotedb":
            for index, peer in enumerate(atomdb.get("remote_peers") or []):
                if isinstance(peer, dict):
                    cls._map_remote_peer(services, peer, index)

    def map_services(self, config_file: dict) -> dict:
        services: dict[str, dict] = {}

        atomdb = config_file.get("atomdb") or {}
        self._map_atomdb_section(services, atomdb)

        agents = config_file.get("agents") or {}
        for agent_key, command_name in AGENT_SERVICE_COMMANDS.items():
            section = agents.get(agent_key)
            if not isinstance(section, dict):
                continue

            self._register_endpoint(services, command_name, section.get("endpoint"))

        return services

    def map_hosts(self, config_file: dict | None = None) -> list[dict]:
        services = self.map_services(config_file) if config_file is not None else self.config_dictionary

        hosts_by_ip: dict[str, dict] = {}

        for service_name, service in services.items():
            host = service.get("host", "")
            if not host or host in LOCAL_HOSTS:
                continue

            if host not in hosts_by_ip:
                hosts_by_ip[host] = {"ip": host, "labels": []}

            hosts_by_ip[host]["labels"].append(service_name)

        return sorted(hosts_by_ip.values(), key=lambda item: item["ip"])
