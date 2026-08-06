import os
from typing import Callable, Dict

from common import Settings
from common.config.store import JsonConfigStore
from settings.config import CURRENT_CONFIGFILE_PATH


class BusNodeCommandRegistry:
    def __init__(self):
        self._commands: Dict[str, Callable[..., str]] = {
            "atomdb-broker": self.cmd_atomdb_broker,
            "query-engine": self.cmd_query_engine,
            "evolution-agent": self.cmd_evolution_agent,
            "link-creation-agent": self.cmd_link_creation_agent,
            "inference-agent": self.cmd_inference_agent,
            "context-broker": self.cmd_context_broker,
            "command-router": self.cmd_command_router,
        }

        self._atomdb_flags: Dict[str, str] = {
            "redis_mongodb": "redismongodb",
            "mork_mongodb": "morkdb",
            "inmemorydb": "inmemorydb",
            "remotedb": "remotedb",
        }

        self._settings = Settings(
            store=JsonConfigStore(os.path.expanduser(CURRENT_CONFIGFILE_PATH))
        )

    def build(self, service, endpoint, ports_range, options, **args):
        handler = self._commands.get(service)

        if not handler:
            raise ValueError(f"No handler registered for service '{service}'")

        return handler(service, endpoint, ports_range, options, **args)

    def _check_atomdb_type_flag(self):
        atomdb_config = self._settings.get("services.database.atomdb_backend")
        flag = self._atomdb_flags.get(atomdb_config)

        return f"--atomdb-type={flag}" if flag else " "

    def _gen_default_cmd(self, service, endpoint, ports_range):
        db_flag = self._check_atomdb_type_flag()

        return f"busnode --service={service} --endpoint={endpoint} --ports-range={ports_range} {db_flag} --config={CURRENT_CONFIGFILE_PATH}".strip()

    def _get_bus_endpoint(self, options):
        hostname = options.get("default_bus_endpoint")
        port = options.get("default_bus_port")

        if not hostname or not port:
            raise ValueError(
                "Query engine endpoint is not configured. Set agents.query.endpoint in the config file."
            )

        return f"{hostname}:{port}"

    def cmd_atomdb_broker(self, service, endpoint, ports_range, options, **args):
        return self._gen_default_cmd(service, endpoint, ports_range)

    def cmd_query_engine(self, service, endpoint, ports_range, options, **args):
        base = self._gen_default_cmd(service, endpoint, ports_range)
        attention_broker = (
            f"{options['attention_broker_hostname']}:{options['attention_broker_port']}"
        )

        return f"{base} --attention-broker-endpoint={attention_broker}"

    def cmd_evolution_agent(self, service, endpoint, ports_range, options, **args):
        base = self._gen_default_cmd(service, endpoint, ports_range)
        attention_broker = (
            f"{options['attention_broker_hostname']}:{options['attention_broker_port']}"
        )
        busnode_endpoint = self._get_bus_endpoint(options)

        return f"{base} --attention-broker-endpoint={attention_broker} --bus-endpoint={busnode_endpoint}"

    def cmd_link_creation_agent(self, service, endpoint, ports_range, options, **args):
        base = self._gen_default_cmd(service, endpoint, ports_range)
        attention_broker = (
            f"{options['attention_broker_hostname']}:{options['attention_broker_port']}"
        )
        busnode_endpoint = self._get_bus_endpoint(options)

        return f"{base} --attention-broker-endpoint={attention_broker} --bus-endpoint={busnode_endpoint}"

    def cmd_inference_agent(self, service, endpoint, ports_range, options, **args):
        base = self._gen_default_cmd(service, endpoint, ports_range)
        attention_broker = (
            f"{options['attention_broker_hostname']}:{options['attention_broker_port']}"
        )
        busnode_endpoint = self._get_bus_endpoint(options)

        return f"{base} --attention-broker-endpoint={attention_broker} --bus-endpoint={busnode_endpoint}"

    def cmd_context_broker(self, service, endpoint, ports_range, options, **args):
        base = self._gen_default_cmd(service, endpoint, ports_range)
        attention_broker = (
            f"{options['attention_broker_hostname']}:{options['attention_broker_port']}"
        )
        busnode_endpoint = self._get_bus_endpoint(options)

        return f"{base} --attention-broker-endpoint={attention_broker} --bus-endpoint={busnode_endpoint}"

    def cmd_command_router(self, service, endpoint, ports_range, options, **args):
        return f"busnode --service=command-router --config={CURRENT_CONFIGFILE_PATH}".strip()
