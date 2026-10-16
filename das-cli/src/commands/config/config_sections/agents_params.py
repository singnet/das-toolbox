from common.command import Command
from common.settings import Settings

BASE_QUERY_DEFAULTS = {
    "unique_assignment_flag": False,
    "attention_update": 0,
    "attention_correlation": 0,
    "attention_focus_strictness": 0.0,
    "max_bundle_size": 1000,
    "max_answers": 0,
    "populate_metta_mapping": False,
    "use_metta_as_query_tokens": False,
    "allow_incomplete_chain_path": False,
}

QUERY_DEFAULTS = {
    "positive_importance_flag": False,
    "disregard_importance_flag": False,
    "unique_value_flag": False,
    "count_flag": False,
}

LINK_CREATION_DEFAULTS = {
    "unique_assignment_flag": False,
    "positive_importance_flag": False,
    "disregard_importance_flag": False,
    "unique_value_flag": False,
    "max_successful_creation_per_round": 10,
    "max_unproductive_visits_per_round": 500,
    "max_visit_attempts_per_round": 20,
    "max_rounds": 5,
    "link_creation_strength_threshold": 0.1,
}

EVOLUTION_DEFAULTS = {
    "population_size": 1000,
    "max_generations": 100,
    "elitism_rate": 0.01,
    "selection_rate": 0.1,
}

CONTEXT_DEFAULTS = {
    "context": "context",
    "use_cache": True,
    "enforce_cache_recreation": False,
    "initial_rent_rate": 0.75,
    "initial_spreading_rate_lowerbound": 0.1,
    "initial_spreading_rate_upperbound": 0.1,
}


def _setup_custom_params(agent_name: str) -> bool:
    return Command.confirm(
        f"Would you like to setup custom parameters for the {agent_name.title()} agent?",
        default=False,
    )


def setup_base_query_params(settings: Settings):
    if not _setup_custom_params("Base Query"):
        return BASE_QUERY_DEFAULTS.copy()

    return {
        "unique_assignment_flag": Command.confirm(
            "Enable unique assignment flag?",
            default=BASE_QUERY_DEFAULTS["unique_assignment_flag"],
        ),
        "attention_update": Command.prompt(
            "Attention update",
            default=BASE_QUERY_DEFAULTS["attention_update"],
            type=int,
        ),
        "attention_correlation": Command.prompt(
            "Attention correlation",
            default=BASE_QUERY_DEFAULTS["attention_correlation"],
            type=int,
        ),
        "attention_focus_strictness": Command.prompt(
            "Attention focus strictness",
            default=BASE_QUERY_DEFAULTS["attention_focus_strictness"],
            type=float,
        ),
        "max_bundle_size": Command.prompt(
            "Max bundle size",
            default=BASE_QUERY_DEFAULTS["max_bundle_size"],
            type=int,
        ),
        "max_answers": Command.prompt(
            "Max answers",
            default=BASE_QUERY_DEFAULTS["max_answers"],
            type=int,
        ),
        "populate_metta_mapping": Command.confirm(
            "Populate MeTTa mapping?",
            default=BASE_QUERY_DEFAULTS["populate_metta_mapping"],
        ),
        "use_metta_as_query_tokens": Command.confirm(
            "Use MeTTa as query tokens?",
            default=BASE_QUERY_DEFAULTS["use_metta_as_query_tokens"],
        ),
        "allow_incomplete_chain_path": Command.confirm(
            "Allow incomplete chain path?",
            default=BASE_QUERY_DEFAULTS["allow_incomplete_chain_path"],
        ),
    }


def setup_query_params(settings: Settings):
    if not _setup_custom_params("Query"):
        return QUERY_DEFAULTS.copy()

    return {
        "positive_importance_flag": Command.confirm(
            "Enable positive importance flag?",
            default=QUERY_DEFAULTS["positive_importance_flag"],
        ),
        "disregard_importance_flag": Command.confirm(
            "Enable disregard importance flag?",
            default=QUERY_DEFAULTS["disregard_importance_flag"],
        ),
        "unique_value_flag": Command.confirm(
            "Enable unique value flag?",
            default=QUERY_DEFAULTS["unique_value_flag"],
        ),
        "count_flag": Command.confirm(
            "Enable count flag?",
            default=QUERY_DEFAULTS["count_flag"],
        ),
    }


def setup_link_creation_params(settings: Settings):
    if not _setup_custom_params("Link Creation"):
        return LINK_CREATION_DEFAULTS.copy()

    return {
        "unique_assignment_flag": Command.confirm(
            "Enable unique assignment flag?",
            default=LINK_CREATION_DEFAULTS["unique_assignment_flag"],
        ),
        "positive_importance_flag": Command.confirm(
            "Enable positive importance flag?",
            default=LINK_CREATION_DEFAULTS["positive_importance_flag"],
        ),
        "disregard_importance_flag": Command.confirm(
            "Enable disregard importance flag?",
            default=LINK_CREATION_DEFAULTS["disregard_importance_flag"],
        ),
        "unique_value_flag": Command.confirm(
            "Enable unique value flag?",
            default=LINK_CREATION_DEFAULTS["unique_value_flag"],
        ),
        "max_successful_creation_per_round": Command.prompt(
            "Max successful creation per round",
            default=LINK_CREATION_DEFAULTS["max_successful_creation_per_round"],
            type=int,
        ),
        "max_unproductive_visits_per_round": Command.prompt(
            "Max unproductive visits per round",
            default=LINK_CREATION_DEFAULTS["max_unproductive_visits_per_round"],
            type=int,
        ),
        "max_visit_attempts_per_round": Command.prompt(
            "Max visit attempts per round",
            default=LINK_CREATION_DEFAULTS["max_visit_attempts_per_round"],
            type=int,
        ),
        "max_rounds": Command.prompt(
            "Max rounds",
            default=LINK_CREATION_DEFAULTS["max_rounds"],
            type=int,
        ),
        "link_creation_strength_threshold": Command.prompt(
            "Link creation strength threshold",
            default=LINK_CREATION_DEFAULTS["link_creation_strength_threshold"],
            type=float,
        ),
    }


def setup_evolution_params(settings: Settings):
    if not _setup_custom_params("Evolution"):
        return EVOLUTION_DEFAULTS.copy()

    return {
        "population_size": Command.prompt(
            "Population size",
            default=EVOLUTION_DEFAULTS["population_size"],
            type=int,
        ),
        "max_generations": Command.prompt(
            "Max generations",
            default=EVOLUTION_DEFAULTS["max_generations"],
            type=int,
        ),
        "elitism_rate": Command.prompt(
            "Elitism rate",
            default=EVOLUTION_DEFAULTS["elitism_rate"],
            type=float,
        ),
        "selection_rate": Command.prompt(
            "Selection rate",
            default=EVOLUTION_DEFAULTS["selection_rate"],
            type=float,
        ),
    }


def setup_context_params(settings: Settings):
    if not _setup_custom_params("Context"):
        return CONTEXT_DEFAULTS.copy()

    return {
        "context": Command.prompt(
            "Context",
            default=CONTEXT_DEFAULTS["context"],
        ),
        "use_cache": Command.confirm(
            "Use cache?",
            default=CONTEXT_DEFAULTS["use_cache"],
        ),
        "enforce_cache_recreation": Command.confirm(
            "Enforce cache recreation?",
            default=CONTEXT_DEFAULTS["enforce_cache_recreation"],
        ),
        "initial_rent_rate": Command.prompt(
            "Initial rent rate",
            default=CONTEXT_DEFAULTS["initial_rent_rate"],
            type=float,
        ),
        "initial_spreading_rate_lowerbound": Command.prompt(
            "Initial spreading rate lowerbound",
            default=CONTEXT_DEFAULTS["initial_spreading_rate_lowerbound"],
            type=float,
        ),
        "initial_spreading_rate_upperbound": Command.prompt(
            "Initial spreading rate upperbound",
            default=CONTEXT_DEFAULTS["initial_spreading_rate_upperbound"],
            type=float,
        ),
    }
