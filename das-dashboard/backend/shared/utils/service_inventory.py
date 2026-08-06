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

ORCHESTRATION_CORE = frozenset({"attention-broker", "query-engine"})


def orchestration_group_for(service_key: str) -> str | None:
    if service_key not in ORCHESTRATION_ORDER:
        return None
    return "core" if service_key in ORCHESTRATION_CORE else "agent"


SERVICE_CATALOG: dict[str, dict] = {
    "query-engine": {
        "display_name": "Query Agent",
        "type": "agent",
    },
    "link-creation-agent": {
        "display_name": "Link Creation Agent",
        "type": "agent",
    },
    "inference-agent": {
        "display_name": "Inference Agent",
        "type": "agent",
    },
    "evolution-agent": {
        "display_name": "Evolution Agent",
        "type": "agent",
    },
    "attention-broker": {
        "display_name": "Attention Broker",
        "type": "broker",
    },
    "context-broker": {
        "display_name": "Context Broker",
        "type": "broker",
    },
    "atomdb-broker": {
        "display_name": "AtomDB Broker",
        "type": "broker",
    },
    "command-router": {
        "display_name": "Command Router",
        "type": "agent",
    },
    "db": {
        "display_name": "MongoDB",
        "type": "atomdb",
    },
    "redis": {
        "display_name": "Redis",
        "type": "atomdb",
    },
    "morkdb": {
        "display_name": "MorkDB",
        "type": "atomdb",
    },
    "adapterdb": {
        "display_name": "AdapterDB",
        "type": "atomdb",
    },
}


def build_service_row(service_key: str, service: dict) -> dict:
    catalog = SERVICE_CATALOG.get(service_key, {})
    port = service.get("port")

    return {
        "key": service_key,
        "displayName": catalog.get("display_name", service_key),
        "type": catalog.get("type", "service"),
        "orchestrationGroup": orchestration_group_for(service_key),
        "host": service.get("host", ""),
        "port": port if port else None,
    }
