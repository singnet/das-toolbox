from common.command import Command
from common.settings import Settings
from .setup_utils import (
    _get_default_value,
)


##########################################
##             PARAMS SETUP             ##
##########################################

def query_agent_params(settings: Settings):
    print("\n[SETUP] Query Agent")

    return {
        "max_answers": Command.prompt(
            "Max answers",
            default=settings.get("params.query.max_answers", _get_default_value("params.query.max_answers")),
            type=int,
        ),
        "max_bundle_size": Command.prompt(
            "Max bundle size",
            default=settings.get("params.query.max_bundle_size", _get_default_value("params.query.max_bundle_size")),
            type=int,
        ),
        "count_flag": Command.confirm(
            "Enable count flag?",
            default=settings.get("params.query.count_flag", _get_default_value("params.query.count_flag")),
        ),
        "attention_update_flag": Command.confirm(
            "Enable attention update?",
            default=settings.get("params.query.attention_update_flag", _get_default_value("params.query.attention_update_flag")),
        ),
        "unique_assignment_flag": Command.confirm(
            "Enable unique assignment?",
            default=settings.get("params.query.unique_assignment_flag", _get_default_value("params.query.unique_assignment_flag")),
        ),
        "positive_importance_flag": Command.confirm(
            "Enable positive importance?",
            default=settings.get("params.query.positive_importance_flag", _get_default_value("params.query.positive_importance_flag")),
        ),
        "populate_metta_mapping": Command.confirm(
            "Populate metta mapping?",
            default=settings.get("params.query.populate_metta_mapping", _get_default_value("params.query.populate_metta_mapping")),
        ),
        "use_metta_as_query_tokens": Command.confirm(
            "Use metta as query tokens?",
            default=settings.get("params.query.use_metta_as_query_tokens", _get_default_value("params.query.use_metta_as_query_tokens")),
        ),
    }


def link_creation_params(settings: Settings):
    print("\n[SETUP] Link Creation Agent")

    return {
        "repeat_count": Command.prompt(
            "Repeat count",
            default=settings.get("params.link_creation.repeat_count", _get_default_value("params.link_creation.repeat_count")),
            type=int,
        ),
        "query_interval": Command.prompt(
            "Query interval",
            default=settings.get("params.link_creation.query_interval", _get_default_value("params.link_creation.query_interval")),
            type=int,
        ),
        "query_timeout": Command.prompt(
            "Query timeout",
            default=settings.get("params.link_creation.query_timeout", _get_default_value("params.link_creation.query_timeout")),
            type=int,
        ),
    }


def evolution_agent(settings: Settings):
    print("\n[SETUP] Evolution Agent")

    return {
        "elitism_rate": Command.prompt(
            "Elitism rate",
            default=settings.get("params.evolution.elitism_rate", _get_default_value("params.evolution.elitism_rate")),
            type=float,
        ),
        "max_generations": Command.prompt(
            "Max generations",
            default=settings.get("params.evolution.max_generations", _get_default_value("params.evolution.max_generations")),
            type=int,
        ),
        "population_size": Command.prompt(
            "Population size",
            default=settings.get("params.evolution.population_size", _get_default_value("params.evolution.population_size")),
            type=int,
        ),
        "selection_rate": Command.prompt(
            "Selection rate",
            default=settings.get("params.evolution.selection_rate", _get_default_value("params.evolution.selection_rate")),
            type=float,
        ),
        "total_attention_tokens": Command.prompt(
            "Total attention tokens",
            default=settings.get("params.evolution.total_attention_tokens", _get_default_value("params.evolution.total_attention_tokens")),
            type=int,
        ),
    }


def context_broker_params(settings: Settings):
    print("\n[SETUP] Context Broker")

    return {
        "context": Command.prompt(
            "Context name",
            default=settings.get("params.context.context", _get_default_value("params.context.context")),
        ),
        "use_cache": Command.confirm(
            "Use cache?",
            default=settings.get("params.context.use_cache", _get_default_value("params.context.use_cache")),
        ),
        "enforce_cache_recreation": Command.confirm(
            "Enforce cache recreation?",
            default=settings.get("params.context.enforce_cache_recreation", _get_default_value("params.context.enforce_cache_recreation")),
        ),
        "initial_rent_rate": Command.prompt(
            "Initial rent rate",
            default=settings.get("params.context.initial_rent_rate", _get_default_value("params.context.initial_rent_rate")),
            type=float,
        ),
        "initial_spreading_rate_lowerbound": Command.prompt(
            "Initial spreading rate lower bound",
            default=settings.get("params.context.initial_spreading_rate_lowerbound", _get_default_value("params.context.initial_spreading_rate_lowerbound")),
            type=float,
        ),
        "initial_spreading_rate_upperbound": Command.prompt(
            "Initial spreading rate upper bound",
            default=settings.get("params.context.initial_spreading_rate_upperbound", _get_default_value("params.context.initial_spreading_rate_upperbound")),
            type=float,
        ),
    }

## MAIN SETUP FUNC ##

def params_config_section(settings: Settings):
    setup_custom_params = Command.confirm(
        "\nWould you like to set-up custom parameters for: Query Agent, Link Creation Agent, Context Broker, Evolution Agent?",
        default = False,
    )

    if setup_custom_params:
        return {
            "params": {
                "query": query_agent_params(settings),
                "link_creation": link_creation_params(settings),
                "evolution": evolution_agent(settings),
                "context": context_broker_params(settings),
            }
        }
    else:
        return {
            "params": _get_default_value("params")
        }
    