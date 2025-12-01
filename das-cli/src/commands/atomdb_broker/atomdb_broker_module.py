from common import Module
from common import Settings
from .atomdb_broker_bus_manager import AtomDbBrokerBusNodeManager
from common.config.store import JsonConfigStore
import os
from settings.config import SECRETS_PATH
from .atomdb_broker_cli import AtomDbBrokerCli

class AtomDbBrokerModule(Module):
    _instance = AtomDbBrokerCli

    def __init__(self):
        super().__init__()

        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

        self._dependecy_injection = [
            (
                AtomDbBrokerBusNodeManager,
                self._bus_node_container_manager_factory,
            ),
            (
                Settings,
                self._settings,
            )
        ]

        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

    def _bus_node_container_manager_factory(self):
        default_container_name = self._settings.get("services.atomdb_broker.container_name")

        mongodb_port = self._settings.get("services.mongodb.port")
        mongodb_username = self._settings.get("services.mongodb.username")
        mongodb_password = self._settings.get("services.mongodb.password")

        redis_port = self._settings.get("services.redis.port")

        morkdb_port = self._settings.get("services.morkdb.port")

        service_name = "atomdb-broker"
        service_port = self._settings.get("services.atomdb_broker.port")
        service_endpoint = f"0.0.0.0:{self._settings.get('services.atomdb_broker.port')}"

        return AtomDbBrokerBusNodeManager(
            default_container_name,
            options={
                "service": service_name,
                "service_port": service_port,
                "service_endpoint": service_endpoint,
                "redis_hostname": "0.0.0.0",
                "redis_port": redis_port,
                "mongodb_port": mongodb_port,
                "mongodb_hostname": "0.0.0.0",
                "mongodb_username": mongodb_username,
                "mongodb_password": mongodb_password,
                "morkdb_port": morkdb_port,
            },
        )