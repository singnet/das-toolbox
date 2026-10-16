from shared.internal.configuration_constants import CONSTANTS
from shared.mappers.das_config_mapper import ConfigMapper
from shared.mappers.nested_config_mapper import NestedConfigMapper
from shared.utils.flat_config_utils import merge_flat_config


def test_dashboard_config_matches_das_1_2_0_schema_and_vault_contract():
    flat_config = merge_flat_config({})
    flat_config["agents.link_creation"].update(
        {
            "repeat_count": 1,
            "query_interval": 0,
            "query_timeout": 0,
            "max_answers": 10,
        }
    )

    config = ConfigMapper.build_config(flat_config)

    assert config["atomdb"]["uid"] == "local"
    assert config["agents"]["schema_version"] == "1.2.0"
    assert config["agents"]["base_proxy"] == {"params": {"orchestration_schema": 0}}
    assert config["vault"] == CONSTANTS["vault"]
    assert set(config["agents"]["base_query"]["params"]) == {
        "unique_assignment_flag",
        "attention_update",
        "attention_correlation",
        "attention_focus_strictness",
        "max_bundle_size",
        "max_answers",
        "populate_metta_mapping",
        "use_metta_as_query_tokens",
        "allow_incomplete_chain_path",
        "public_key_tokens",
    }
    assert set(config["agents"]["link_creation"]["params"]) == {
        "unique_assignment_flag",
        "positive_importance_flag",
        "disregard_importance_flag",
        "unique_value_flag",
        "max_successful_creation_per_round",
        "max_unproductive_visits_per_round",
        "max_visit_attempts_per_round",
        "max_rounds",
        "link_creation_strength_threshold",
    }
    assert set(config["agents"]["query"]["params"]) == {
        "positive_importance_flag",
        "disregard_importance_flag",
        "unique_value_flag",
        "count_flag",
    }
    assert set(config["agents"]["evolution"]["params"]) == {
        "population_size",
        "max_generations",
        "elitism_rate",
        "selection_rate",
    }
    assert set(config["agents"]["context"]["params"]) == {
        "context",
        "use_cache",
        "enforce_cache_recreation",
        "initial_rent_rate",
        "initial_spreading_rate_lowerbound",
        "initial_spreading_rate_upperbound",
    }
    flat_round_trip = NestedConfigMapper.to_flat(config)
    assert flat_round_trip["atomdb"]["atomdb_uid"] == "local"
    assert flat_round_trip["agents.base_proxy"] == {"orchestration_schema": 0}
    assert flat_round_trip["vault"] == CONSTANTS["vault"]