from common.command import Command
from common.settings import Settings
from common.prompt_types import PortRangeType
from common.settings import Settings
from .setup_utils import _extract_port, _get_default_value


########################################
##            AGENTS SETUP            ##
########################################

def agents_port_setup(settings: Settings, agent_name: str):
    agent_label = agent_name.replace("_", " ").title()

    agent_port = Command.prompt(
        f"Enter the {agent_label} Agent port",
        default=_extract_port(settings.get(f"agents.{agent_name}.endpoint", _get_default_value(f"agents.{agent_name}.endpoint"))),
    )

    agent_port_range = Command.prompt(
        f"Enter the {agent_label} Agent ports range",
        default=settings.get(f"agents.{agent_name}.ports_range", _get_default_value(f"agents.{agent_name}.ports_range")),
        type=PortRangeType()
    )

    return {
        agent_name: {
            "endpoint": f"localhost:{agent_port}",
            "ports_range": agent_port_range,
        }
    }

## MAIN SETUP FUNC ##

def agents_config_section(settings: Settings):
    agents = ["query", "link_creation", "inference", "evolution"]
    agents_setup = dict()

    for agent in agents:
        agents_setup.update(agents_port_setup(settings, agent))

    return {
        "agents": agents_setup
    }
