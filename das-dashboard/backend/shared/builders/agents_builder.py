from shared.builders.builder_helpers import _get, _require
from shared.internal.configuration_constants import (
    AGENTS_SCHEMA_VERSION,
    COMMAND_ROUTER_HTTP_API_DEFAULTS,
)
from shared.utils.path_utils import replace_endpoint_port


class AgentsBuilder:

    # Final JSON key order under "agents"
    AGENT_KEYS = (
        "attention",
        "base_query",
        "query",
        "link_creation",
        "inference",
        "evolution",
        "context",
        "atomdb",
        "command_router",
    )

    CONNECTION_KEYS = frozenset({"endpoint", "ports_range"})

    UI_CONNECTION_KEYS = frozenset({
        "endpoint_ip",
        "endpoint_port",
        "ports_range_start",
        "ports_range_end",
        "http_api_port",
    })

    EXCLUDED_PARAM_KEYS = CONNECTION_KEYS | UI_CONNECTION_KEYS

    _BASE_QUERY_PARAMS = (
        "max_answers",
        "max_bundle_size",
        "attention_update",
        "attention_correlation",
        "attention_focus_strictness",
        "unique_assignment_flag",
        "use_link_template_cache",
        "populate_metta_mapping",
        "use_metta_as_query_tokens",
        "allow_incomplete_chain_path",
    )

    _QUERY_PARAMS = (
        "positive_importance_flag",
        "disregard_importance_flag",
        "unique_value_flag",
        "count_flag",
    )

    _LINK_CREATION_PARAMS = (
        "max_answers",
        "repeat_count",
        "context",
        "attention_update",
        "attention_correlation",
        "query_interval",
        "query_timeout",
        "positive_importance_flag",
        "use_metta_as_query_tokens",
    )

    _INFERENCE_PARAMS = (
        "inference_request_timeout",
        "repeat_count",
        "max_answers",
    )

    _EVOLUTION_PARAMS = (
        "population_size",
        "max_generations",
        "elitism_rate",
        "selection_rate",
    )

    _CONTEXT_PARAMS = (
        "context",
        "initial_rent_rate",
        "initial_spreading_rate_lowerbound",
        "initial_spreading_rate_upperbound",
        "use_cache",
        "enforce_cache_recreation",
    )

    def build(self, dto: dict) -> dict:
        agents = {
            "schema_version": AGENTS_SCHEMA_VERSION,
        }

        for agent_key in self.AGENT_KEYS:
            section = _get(dto, f"agents.{agent_key}")
            if section:
                agents[agent_key] = self.build_agent(agent_key, section)

        return agents

    def build_agent(self, agent_key: str, agent: dict) -> dict:
        label = f"agents.{agent_key}"

        if agent_key == "base_query":
            return self._build_base_query(agent, label)

        if agent_key == "attention":
            return self._build_attention(agent, label)

        if agent_key == "command_router":
            return self._build_command_router(agent, label)

        if agent_key == "atomdb":
            return self._build_connection_only(agent, label)

        if agent_key == "query":
            return self._build_connection_and_params(
                agent,
                label,
                param_keys=self._QUERY_PARAMS,
            )

        if agent_key == "link_creation":
            return self._build_connection_and_params(
                agent,
                label,
                param_keys=self._LINK_CREATION_PARAMS,
            )

        if agent_key == "inference":
            return self._build_connection_and_params(
                agent,
                label,
                param_keys=self._INFERENCE_PARAMS,
            )

        if agent_key == "evolution":
            return self._build_connection_and_params(
                agent,
                label,
                param_keys=self._EVOLUTION_PARAMS,
            )

        if agent_key == "context":
            return self._build_connection_and_params(
                agent,
                label,
                param_keys=self._CONTEXT_PARAMS,
            )

        raise ValueError(f"Unsupported agent key: {agent_key}")

    @classmethod
    def _normalize_base_query(cls, agent: dict) -> dict:
        normalized = {}

        for key, value in agent.items():
            if key.startswith("agents.base_query.params."):
                normalized[key.removeprefix("agents.base_query.params.")] = value
            elif key.startswith("base_query.params."):
                normalized[key.removeprefix("base_query.params.")] = value
            else:
                normalized[key] = value

        return normalized

    @classmethod
    def _split_connection_and_params(cls, agent: dict) -> tuple[dict, dict]:
        connection = {}
        params = {}

        for key, value in agent.items():
            if key in cls.CONNECTION_KEYS:
                connection[key] = value
            elif key not in cls.EXCLUDED_PARAM_KEYS:
                params[key] = value

        return connection, params

    @classmethod
    def _build_base_query(cls, agent: dict, label: str) -> dict:
        normalized = cls._normalize_base_query(agent)
        _require(normalized, *cls._BASE_QUERY_PARAMS, label=label)
        params = dict(normalized)
        params["attention_focus_strictness"] = float(
            params.get("attention_focus_strictness", 0.0)
        )
        return {"params": params}

    @classmethod
    def _build_attention(cls, agent: dict, label: str) -> dict:
        _require(agent, "endpoint", label=label)
        return {"endpoint": _get(agent, "endpoint")}

    @classmethod
    def _build_command_router(cls, agent: dict, label: str) -> dict:
        _require(agent, "endpoint", "ports_range", "http_api_port", label=label)

        http_api_endpoint = replace_endpoint_port(
            _get(agent, "endpoint"),
            _get(agent, "http_api_port"),
        )

        return {
            "endpoint": _get(agent, "endpoint"),
            "ports_range": _get(agent, "ports_range"),
            "http_api": {
                "endpoint": http_api_endpoint,
                **COMMAND_ROUTER_HTTP_API_DEFAULTS,
            },
        }

    @classmethod
    def _build_connection_only(cls, agent: dict, label: str) -> dict:
        _require(agent, "endpoint", "ports_range", label=label)
        return {
            "endpoint": _get(agent, "endpoint"),
            "ports_range": _get(agent, "ports_range"),
        }

    @classmethod
    def _build_connection_and_params(
        cls,
        agent: dict,
        label: str,
        *,
        param_keys: tuple[str, ...],
    ) -> dict:
        _require(agent, "endpoint", "ports_range", *param_keys, label=label)

        connection, params = cls._split_connection_and_params(agent)

        return {
            **connection,
            "params": params,
        }
