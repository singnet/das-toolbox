from common.command import Command
from common.settings import Settings
from common.prompt_types import PortRangeType
from common.settings import Settings
from .setup_utils import get_default_value
from common.utils import extract_service_port

#########################################
##            BROKERS SETUP            ##
#########################################

def brokers_port_setup(settings: Settings, broker_name: str):
    broker_label = broker_name.replace("_", " ").title()

    broker_port = Command.prompt(
        f"Enter the {broker_label} Broker port",
        default=extract_service_port(get_default_value(settings, f"brokers.{broker_name}.endpoint")),
    )

    broker_port_range = None if broker_name == "attention" else Command.prompt(
        f"Enter the {broker_label} Broker ports range",
        default=get_default_value(settings, f"brokers.{broker_name}.ports_range"),
        type=PortRangeType(),
    )

    if broker_port_range is None:
        return {
            broker_name: {
                "endpoint": f"localhost:{broker_port}"
            }
        }

    else:
        return {
            broker_name: {
                "endpoint": f"localhost:{broker_port}",
                "ports_range": broker_port_range,
            }
        }
    
## SETUP MAIN FUNC ##

def brokers_config_section(settings: Settings):
    brokers = ["attention", "context", "atomdb"]
    brokers_setup = dict()

    for broker in brokers:
        brokers_setup.update(brokers_port_setup(settings, broker))

    return {
        "brokers": brokers_setup
    }