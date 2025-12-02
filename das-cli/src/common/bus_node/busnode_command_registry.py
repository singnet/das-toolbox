from typing import Dict, Callable

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
    
    def build(self, service, endpoint, ports_range, options, **args):

        handler = self._commands.get(service)

        if not handler:
            raise ValueError(f"No handler registered for service '{service}'")
        else:
            cmd = handler(service, endpoint, ports_range, options, **args)

            return cmd
        

    def _gen_default_cmd(self, service, endpoint, ports_range):

        return f"busnode --service={service} --endpoint={endpoint} --ports-range={ports_range}"

    def _cmd_atomdb_broker(self, service, endpoint, ports_range, options, **args):

        base = self._gen_default_cmd(service, endpoint, ports_range)

        return base

    def _cmd_query_engine(self, service, endpoint, ports_range, options, **args):

        base = self._gen_default_cmd(service, endpoint, ports_range)
        attention_broker = f"{options['attention_broker_hostname']}:{options['attention_broker_port']}"

        return f"{base} --attention-broker-endpoint={attention_broker}"

    def _cmd_evolution_agent(self, service, endpoint, ports_range, options, **args):

        base = self._gen_default_cmd(service, endpoint, ports_range)

        attention_broker = f"{options['attention_broker_hostname']}:{options['attention_broker_port']}"
        busnode_endpoint = f"{args['peer_hostname']}:{args['peer_port']}"

        return f"{base} --attention-broker-endpoint={attention_broker} --busnode-endpoint={busnode_endpoint}"

    def _cmd_link_creation_agent(self, service, endpoint, ports_range, options, **args):

        base = self._gen_default_cmd(service, endpoint, ports_range)
        
        attention_broker = f"{options['attention_broker_hostname']}:{options['attention_broker_port']}"
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