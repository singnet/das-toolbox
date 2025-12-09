from typing import Dict, Callable
from common import Settings
from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH 
import os

class BusNodeCommandRegistry:

    def __init__(self):
        self._commands: Dict[str, Callable[..., str]] = {
            "atomdb-broker": self._cmd_atomdb_broker,
            "query-engine": self._cmd_query_engine,
            "evolution-agent": self._cmd_evolution_agent,
            "link-creation-agent": self._cmd_link_creation_agent,
            "inference-agent": self._cmd_inference_agent,
            "context-broker": self._cmd_context_broker,
        }
        
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

    def build(self, service, endpoint, ports_range, options, **args):

        handler = self._commands.get(service)

        if not handler:
            raise ValueError(f"No handler registered for service '{service}'")
        else:
            cmd = handler(service, endpoint, ports_range, options, **args)

            return cmd

    def _check_using_morkdb(self):
        atomdb = self._settings.get("services.database.atomdb_backend")

        return "--use-mork" if atomdb == "mork_mongodb" else " "

    def _gen_default_cmd(self, service, endpoint, ports_range):
        use_mork = self._check_using_morkdb()

        return f"busnode --service={service} --endpoint={endpoint} --ports-range={ports_range} {use_mork}".strip()

    def _cmd_atomdb_broker(self, service, endpoint, ports_range, options, **args):

        base = self._gen_default_cmd(service, endpoint, ports_range)

        return base

    def _cmd_query_engine(self, service, endpoint, ports_range, options, **args):

        base = self._gen_default_cmd(service, endpoint, ports_range)
        attention_broker = (
            f"{options['attention_broker_hostname']}:{options['attention_broker_port']}"
        )

        return f"{base} --attention-broker-endpoint={attention_broker}"

    def _cmd_evolution_agent(self, service, endpoint, ports_range, options, **args):

        base = self._gen_default_cmd(service, endpoint, ports_range)

        attention_broker = (
            f"{options['attention_broker_hostname']}:{options['attention_broker_port']}"
        )
        busnode_endpoint = f"{args['peer_hostname']}:{args['peer_port']}"

        return f"{base} --attention-broker-endpoint={attention_broker} --busnode-endpoint={busnode_endpoint}"

    def _cmd_link_creation_agent(self, service, endpoint, ports_range, options, **args):

        base = self._gen_default_cmd(service, endpoint, ports_range)

        attention_broker = (
            f"{options['attention_broker_hostname']}:{options['attention_broker_port']}"
        )
        busnode_endpoint = f"{args['peer_hostname']}:{args['peer_port']}"

        return f"{base} --attention-broker-endpoint={attention_broker} --busnode-endpoint={busnode_endpoint}"

    def _cmd_inference_agent(self, service, endpoint, ports_range, options, **args):

        base = self._gen_default_cmd(service, endpoint, ports_range)
        
        attention_broker = f"{options['attention_broker_hostname']}:{options['attention_broker_port']}"
        busnode_endpoint = f"{args['peer_hostname']}:{args['peer_port']}"

        return f"{base} --attention-broker-endpoint={attention_broker} --busnode-endpoint={busnode_endpoint}"
    
    def _cmd_context_broker(self, service, endpoint, ports_range, options, **args):

        base = self._gen_default_cmd(service, endpoint, ports_range)
        
        attention_broker = f"{options['attention_broker_hostname']}:{options['attention_broker_port']}"
        busnode_endpoint = f"{args['peer_hostname']}:{args['peer_port']}"

        return f"{base} --attention-broker-endpoint={attention_broker} --busnode-endpoint={busnode_endpoint}"
