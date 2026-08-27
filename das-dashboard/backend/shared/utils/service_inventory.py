ORCHESTRATION_ORDER = (
    "attention-broker",
    "query-engine",
    "atomdb-broker",
    "command-router",
    "context-broker",
    "link-creation-agent",
    "evolution-agent",
    "inference-agent",
)


def build_initial_state(web_config) -> dict:
    return {"hosts": web_config.map_dashboard_hosts()}
