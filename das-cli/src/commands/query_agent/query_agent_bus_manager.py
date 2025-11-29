from typing import Dict

from common import ContainerImageMetadata
from common.bus_node.busnode_container_manager import BusNodeContainerManager
from common.docker import Container
from settings.config import DAS_IMAGE_NAME, DAS_IMAGE_VERSION


class QueryAgentBusNodeManager(BusNodeContainerManager):

    def __init__(self, default_container_name: str, options: Dict = {}):

        self._options = options

        container = Container(
            default_container_name,
            metadata={
                "port": options.get("service_port"),
                "image": ContainerImageMetadata(
                    {
                        "name": DAS_IMAGE_NAME,
                        "version": DAS_IMAGE_VERSION,
                    }
                ),
            },
        )

        super().__init__(container, options)

    def _gen_bus_node_command(self, service, endpoint, ports_range, **kwargs):
        default_cmd = super()._gen_default_bus_node_command(
            service, endpoint, ports_range, **kwargs
        )

        attention_broker_endpoint = f"{self._options.get('attention_broker_hostname')}:{self._options.get('attention_broker_port')}"

        return f"{default_cmd} --attention-broker-endpoint={attention_broker_endpoint}"
