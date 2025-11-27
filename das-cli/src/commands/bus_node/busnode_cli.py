from common import Command, CommandGroup, CommandOption, Settings, StdoutSeverity, StdoutType
from .busnode_container_manager import BusNodeContainerManager
from injector import inject


class StartBusNodeCommand(Command):

    name = "start"
    
    help = """

NAME

    start 

SYNOPSIS

    das-cli bus-node start

DESCRIPTION

    This command starts a bus-node running a specified service.

EXAMPLES

    To start a bus node for the Context Broker service:
    das-cli bus-node start --service context-broker --endpoint localhost:1026 --port-range 46000:46999

"""

    params = [
        #Required params for every bus-node
        CommandOption(
            ["--service"],
            help="Service to be instantiated via bus node (eg. context-broker, attention-broker)",
            type=str,
            required=True,
        ),
        CommandOption(
            ["--endpoint"],
            help="Endpoint to be used by the bus node (eg. 0.0.0.0:1234)",
            type=str,
            required=True,
        ),
        CommandOption(
            ["--ports-range"],
            help="Port range for the bus node to use (eg. 46000:46999)",
            type=str,
            required=True,
        ),

    ]

    @inject
    def __init__(self,
                busnode_container_manager: BusNodeContainerManager
            ):
        
        super().__init__()
        self._busnode_container_manager = busnode_container_manager


    def _get_default_container(self):
        return BusNodeContainerManager.get_container()


    def _start_bus_node(self,
                        service,
                        endpoint,
                        ports_range,
                        **kwargs
                    ) -> str:
        
        container = self._busnode_container_manager.start_container(service, endpoint, ports_range, **kwargs)
        return container

    def run(
            self,
            service,
            endpoint,
            ports_range,
            **kwargs
        ):

        print(kwargs)

        self.stdout(f"Starting bus-node for service {service} at {endpoint} with port range {ports_range}...")

        container = self._start_bus_node(service, endpoint, ports_range, **kwargs)

        if container is not None:
            self.stdout(f"Bus-node for service {service} started successfully.", StdoutSeverity.SUCCESS)
        else:
            self.stdout(f"Failed to start bus-node for service {service}.", StdoutSeverity.ERROR)

class StopBusNodeCommand(Command):

    name = "stop"

    help = """

NAME

    stop - stop a specified busnode

SYNOPSIS

    das-cli bus-node stop

DESCRIPTION

    This command stops a specified bus-node running a service.

EXAMPLES

    To stop a running bus-node:

    $ das-cli bus-node stop --node-name bus-node-context-broker-0

"""

    params = [
        CommandOption(
            ["--node-name"],
            help="Name of the bus-node to stop",
            type=str,
            required=True,
        )
    ]

    @inject
    def __init__(self, busnode_container_manager: BusNodeContainerManager):
        super().__init__()
        self._busnode_container_manager = busnode_container_manager

    def _stop_bus_node(self, node_name: str):
        self._busnode_container_manager.stop(node_name)

    def run(
            self,
            node_name: str
        ):

        self.stdout(f"Stopping bus-node with name {node_name}...")
        self._stop_bus_node(node_name)

        self.stdout(f"Bus-node {node_name} stopped successfully.", StdoutSeverity.SUCCESS)



class BusNodeCli(CommandGroup):

    name = "bus-node"

    help = """

        Commands to manage the bus nodes

    """

    @inject
    def __init__(self, StartBusNodeCommand: StartBusNodeCommand, StopBusNodeCommand: StopBusNodeCommand):
        super().__init__()
        self.add_commands([
            StartBusNodeCommand,
            StopBusNodeCommand
        ])