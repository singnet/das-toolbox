import json
import os

from shared.exceptions.custom_exceptions import (
    ConfigurationFileLoadError,
    ConfigurationValueNotFoundError,
)
from shared.internal.constants import (
    CONFIG_PATH,
    DEFAULT_WEBPROFILE_PATH as PROFILE_PATH,
    LOCAL_HOSTS,
    LOCAL_DASHBOARD_HOST,
)
from shared.utils.service_inventory import build_service_row

# Agent section keys mapped to das-cli service command names.
AGENT_SERVICE_COMMANDS = {
    "attention": "attention-broker",
    "query": "query-agent",
    "link_creation": "link-creation-agent",
    "inference": "inference-agent",
    "evolution": "evolution-agent",
    "context": "context-broker",
    "atomdb": "atomdb-broker",
    "command_router": "command-router",
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
        except Exception:
            self.user_profile = {}

    def load_config_dictionary(self, config: dict | None = None, *, required: bool = True) -> None:
        if config is not None:
            self._validate_nested_config(config)
            self.config_dictionary = self._build_service_map(config)
            return

        if not os.path.exists(CONFIG_PATH):
            if required:
                raise ConfigurationFileLoadError(f"Configuration file not found: {CONFIG_PATH}")
            self.config_dictionary = {}
            return

        try:
            with open(CONFIG_PATH, "r") as config_file:
                loaded = json.load(config_file)
        except json.JSONDecodeError as error:
            raise ConfigurationFileLoadError(
                f"Invalid JSON in configuration file: {error}"
            ) from error
        except OSError as error:
            raise ConfigurationFileLoadError(
                f"Could not read configuration file: {error}"
            ) from error

        if isinstance(loaded, list):
            if not loaded:
                raise ConfigurationFileLoadError("Configuration file is empty.")
            loaded = loaded[0]

        self._validate_nested_config(loaded)
        self.config_dictionary = self._build_service_map(loaded)

    def load_raw_configuration(self) -> dict:
        if not os.path.exists(CONFIG_PATH):
            raise ConfigurationFileLoadError(f"Configuration file not found: {CONFIG_PATH}")

        try:
            with open(CONFIG_PATH, "r") as file:
                loaded = json.load(file)
        except json.JSONDecodeError as error:
            raise ConfigurationFileLoadError(
                f"Invalid JSON in configuration file: {error}"
            ) from error
        except OSError as error:
            raise ConfigurationFileLoadError(
                f"Could not read configuration file: {error}"
            ) from error

        if isinstance(loaded, list):
            if not loaded:
                raise ConfigurationFileLoadError("Configuration file is empty.")
            loaded = loaded[0]

        self._validate_nested_config(loaded)
        return loaded

    def get_service_config(self, service_key: str, *, required: bool = True) -> dict | None:
        service = self.config_dictionary.get(service_key)
        if not service or not service.get("host"):
            if required:
                raise ConfigurationValueNotFoundError(service_key)
            return None
        return service

    def require_config_dictionary(self) -> dict[str, dict]:
        if not self.config_dictionary:
            raise ConfigurationFileLoadError("Configuration has not been loaded.")
        return self.config_dictionary

    def map_remote_hosts(self) -> list[dict]:
        _, remote_by_host = self._group_services_by_host(self.require_config_dictionary())

        return [
            {"ip": host, "labels": [service_key for service_key, _ in entries]}
            for host, entries in sorted(remote_by_host.items(), key=lambda item: item[0])
        ]

    def map_dashboard_hosts(self) -> list[dict]:
        local_entries, remote_by_host = self._group_services_by_host(
            self.require_config_dictionary()
        )

        dashboard_hosts = [
            {
                "ip": host,
                "services": [
                    build_service_row(service_key, service)
                    for service_key, service in entries
                ],
            }
            for host, entries in sorted(remote_by_host.items(), key=lambda item: item[0])
        ]

        if local_entries:
            dashboard_hosts.insert(
                0,
                {
                    "ip": LOCAL_DASHBOARD_HOST,
                    "services": [
                        build_service_row(service_key, service)
                        for service_key, service in local_entries
                    ],
                },
            )

        return dashboard_hosts

    @staticmethod
    def _validate_nested_config(config) -> None:
        if not isinstance(config, dict):
            raise ConfigurationFileLoadError("Configuration must be a JSON object.")

        if "atomdb" not in config or "agents" not in config:
            raise ConfigurationFileLoadError(
                "Configuration must include 'atomdb' and 'agents' sections."
            )

    @classmethod
    def _build_service_map(cls, config_file: dict) -> dict[str, dict]:
        services: dict[str, dict] = {}

        atomdb = config_file.get("atomdb") or {}
        cls._map_atomdb_section(services, atomdb)

        agents = config_file.get("agents") or {}
        for agent_key, command_name in AGENT_SERVICE_COMMANDS.items():
            section = agents.get(agent_key)
            if not isinstance(section, dict):
                continue

            cls._register_endpoint(services, command_name, section.get("endpoint"))

        return services

    @staticmethod
    def _group_services_by_host(
        services: dict[str, dict],
    ) -> tuple[list[tuple[str, dict]], dict[str, list[tuple[str, dict]]]]:
        local_entries: list[tuple[str, dict]] = []
        remote_by_host: dict[str, list[tuple[str, dict]]] = {}

        for service_key, service in services.items():
            host = service.get("host", "")
            if not host:
                continue

            entry = (service_key, service)
            if host in LOCAL_HOSTS:
                local_entries.append(entry)
                continue

            remote_by_host.setdefault(host, []).append(entry)

        return local_entries, remote_by_host

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
    def _register_cluster_nodes(
        cls,
        services: dict,
        nodes: list | None,
        *,
        prefix: str,
        enabled: bool = False,
    ) -> None:
        if not enabled or not isinstance(nodes, list):
            return

        for index, node in enumerate(nodes):
            if not isinstance(node, dict):
                continue

            ip = (node.get("ip") or "").strip()
            if ip:
                cls._register_endpoint(services, f"{prefix}-node-{index}", f"{ip}:0")

    @classmethod
    def _map_redis_mongo(cls, services: dict, section: dict, *, db_name: str = "db") -> None:
        redis = section.get("redis") or {}
        mongo = section.get("mongodb") or {}

        cls._register_endpoint(services, db_name, mongo.get("endpoint"))
        cls._register_endpoint(services, "redis", redis.get("endpoint"))
        cls._register_cluster_nodes(
            services,
            redis.get("nodes"),
            prefix=f"{db_name}-redis",
            enabled=bool(redis.get("cluster")),
        )
        cls._register_cluster_nodes(
            services,
            mongo.get("nodes"),
            prefix=f"{db_name}-mongo",
            enabled=bool(mongo.get("cluster")),
        )

    @classmethod
    def _map_mork_mongo(cls, services: dict, section: dict, *, db_name: str = "db") -> None:
        mongo = section.get("mongodb") or {}
        mork = section.get("morkdb") or {}

        cls._register_endpoint(services, db_name, mongo.get("endpoint"))
        cls._register_endpoint(services, "morkdb", mork.get("endpoint"))
        cls._register_cluster_nodes(
            services,
            mongo.get("nodes"),
            prefix=f"{db_name}-mongo",
            enabled=bool(mongo.get("cluster")),
        )

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
