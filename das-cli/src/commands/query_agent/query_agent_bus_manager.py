
from common.bus_node.busnode_container_manager import BusNodeContainerManager
from typing import Dict

class QueryAgentBusNodeManager(BusNodeContainerManager):

    def __init__(
            self,
            default_container_name:str, 
            options: Dict = {}
        ):
        super().__init__(default_container_name, options)

    def _gen_bus_node_command(self, service, endpoint, ports_range, **kwargs):
        default_cmd = super()._gen_default_bus_node_command(service, endpoint, ports_range, **kwargs)

        attention_broker_endpoint = f"{self._options.get("attention_broker_hostname")}:{self._options.get("attention_broker_port")}"

        return f"{default_cmd} --attention-broker-endpoint={attention_broker_endpoint}"
