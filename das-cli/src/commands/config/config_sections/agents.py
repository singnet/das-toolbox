from common.command import Command
from common.prompt_types import PortRangeType
from common.settings import Settings
from common.utils import extract_service_hostname, extract_service_port

from .agents_params import (
    _setup_custom_params,
    setup_base_query_params,
    setup_context_params,
    setup_evolution_params,
    setup_inference_params,
    setup_link_creation_params,
    setup_query_params,
)
from .setup_utils import get_default_value


def setup_endpoint(settings: Settings, agent_name: str, agent_key: str):

    default_endpoint = str(get_default_value(settings, f"agents.{agent_key}.endpoint"))

    hostname = Command.prompt(
        f"Enter {agent_name.title()}'s hostname",
        default=extract_service_hostname(default_endpoint),
    )

    port = Command.prompt(
        f"Enter {agent_name.title()}'s port",
        default=extract_service_port(default_endpoint),
        type=int,
    )

    return f"{hostname}:{port}"


def setup_ports_range(settings: Settings, agent_name: str, agent_key: str):
    return Command.prompt(
        f"Enter {agent_name.title()}'s ports range",
        default=get_default_value(settings, f"agents.{agent_key}.ports_range"),
        type=PortRangeType(),
    )


def setup_agents_base_params(settings: Settings):
    confirmParameterConfig = Command.confirm(
        "Would you like to set base query parameters for the query agent?", default=False
    )

    if confirmParameterConfig:
        return {"params": setup_base_query_params(settings)}

    return {"params": get_default_value(settings, "agents.base_query.params")}


def setup_attention_broker(settings: Settings):
    endpoint = setup_endpoint(
        settings,
        "attention broker",
        "attention",
    )

    return {
        "endpoint": endpoint,
    }


def setup_query_agent(settings: Settings):
    endpoint = setup_endpoint(
        settings,
        "query agent",
        "query",
    )

    ports_range = setup_ports_range(
        settings,
        "query agent",
        "query",
    )

    confirm_parameter_config = _setup_custom_params("query agent")

    query_params = (
        setup_query_params(settings)
        if confirm_parameter_config
        else get_default_value(settings, "agents.query.params")
    )

    return {
        "endpoint": endpoint,
        "ports_range": ports_range,
        "params": query_params,
    }


def setup_link_creation_agent(settings: Settings):
    endpoint = setup_endpoint(
        settings,
        "link creation agent",
        "link_creation",
    )

    ports_range = setup_ports_range(
        settings,
        "link creation agent",
        "link_creation",
    )

    confirm_parameter_config = _setup_custom_params("link creation agent")

    link_creation_params = (
        setup_link_creation_params(settings)
        if confirm_parameter_config
        else get_default_value(settings, "agents.link_creation.params")
    )

    return {
        "endpoint": endpoint,
        "ports_range": ports_range,
        "params": link_creation_params,
    }


def setup_inference_agent(settings: Settings):
    endpoint = setup_endpoint(
        settings,
        "inference agent",
        "inference",
    )

    ports_range = setup_ports_range(
        settings,
        "inference agent",
        "inference",
    )

    confirm_parameter_config = _setup_custom_params("inference agent")

    inference_params = (
        setup_inference_params(settings)
        if confirm_parameter_config
        else get_default_value(settings, "agents.inference.params")
    )

    return {
        "endpoint": endpoint,
        "ports_range": ports_range,
        "params": inference_params,
    }


def setup_evolution_agent(settings: Settings):
    endpoint = setup_endpoint(
        settings,
        "evolution agent",
        "evolution",
    )

    ports_range = setup_ports_range(
        settings,
        "evolution agent",
        "evolution",
    )

    confirm_parameter_config = _setup_custom_params("evolution agent")

    evolution_params = (
        setup_evolution_params(settings)
        if confirm_parameter_config
        else get_default_value(settings, "agents.evolution.params")
    )

    return {
        "endpoint": endpoint,
        "ports_range": ports_range,
        "params": evolution_params,
    }


def setup_context_broker(settings: Settings):
    endpoint = setup_endpoint(
        settings,
        "context broker",
        "context",
    )

    ports_range = setup_ports_range(
        settings,
        "context broker",
        "context",
    )

    confirm_parameter_config = _setup_custom_params("context broker")

    context_params = (
        setup_context_params(settings)
        if confirm_parameter_config
        else get_default_value(settings, "agents.context.params")
    )

    return {
        "endpoint": endpoint,
        "ports_range": ports_range,
        "params": context_params,
    }


def setup_atomdb_broker(settings: Settings):
    endpoint = setup_endpoint(
        settings,
        "atomdb broker",
        "atomdb",
    )

    ports_range = setup_ports_range(
        settings,
        "atomdb broker",
        "atomdb",
    )

    return {
        "endpoint": endpoint,
        "ports_range": ports_range,
    }


def setup_command_router(settings: Settings):

    endpoint = setup_endpoint(
        settings,
        "command router",
        "command_router",
    )

    ports_range = setup_ports_range(
        settings,
        "command router",
        "command_router",
    )

    return {
        "endpoint": endpoint,
        "ports_range": ports_range,
        "http_api": get_default_value(settings, "agents.command_router.http_api"),
    }


def agents_config_section(settings: Settings):
    return {
        "agents": {
            "schema_version": get_default_value(settings, "agents.schema_version"),
            "attention": setup_attention_broker(settings),
            "base_query": setup_agents_base_params(settings),
            "query": setup_query_agent(settings),
            "link_creation": setup_link_creation_agent(settings),
            "inference": setup_inference_agent(settings),
            "evolution": setup_evolution_agent(settings),
            "context": setup_context_broker(settings),
            "atomdb": setup_atomdb_broker(settings),
            "command_router": setup_command_router(settings),
        }
    }
