from typing import Any

RESERVED_ROUTER_PARAM_KEYS = frozenset({"query"})


def build_query_execution_payload(
    query_text: str,
    parameters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    trimmed = query_text.strip()
    if not trimmed:
        raise ValueError("Query text must not be empty.")

    params: dict[str, Any] = {
        "query": {
            "syntax": "metta",
            "tokens": [trimmed],
        }
    }

    if parameters:
        params.update(normalize_router_parameters(parameters))

    return {"command": "query", "params": params}


def normalize_router_parameters(parameters: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}

    for key, value in parameters.items():
        if key in RESERVED_ROUTER_PARAM_KEYS:
            raise ValueError(f"Reserved parameter '{key}' cannot be overridden.")

        if isinstance(value, bool):
            normalized[key] = value
        elif isinstance(value, int):
            normalized[key] = value
        elif isinstance(value, float):
            normalized[key] = value
        elif isinstance(value, str):
            normalized[key] = value
        else:
            normalized[key] = value

    return normalized
