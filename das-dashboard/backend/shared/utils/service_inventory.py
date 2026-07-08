from shared.enums.das_services import DASServices

SERVICE_CATALOG: dict[str, dict] = {
    "query-agent": {
        "display_name": "Query Agent",
        "type": "agent",
        "patterns": ["das-query-engine"],
    },
    "link-creation-agent": {
        "display_name": "Link Creation Agent",
        "type": "agent",
        "patterns": ["das-link-creation-agent"],
    },
    "inference-agent": {
        "display_name": "Inference Agent",
        "type": "agent",
        "patterns": ["das-inference-agent"],
    },
    "evolution-agent": {
        "display_name": "Evolution Agent",
        "type": "agent",
        "patterns": ["das-evolution-agent"],
    },
    "attention-broker": {
        "display_name": "Attention Broker",
        "type": "broker",
        "patterns": ["das-attention-broker"],
    },
    "context-broker": {
        "display_name": "Context Broker",
        "type": "broker",
        "patterns": ["das-context-broker"],
    },
    "atomdb-broker": {
        "display_name": "AtomDB Broker",
        "type": "broker",
        "patterns": ["das-atomdb-broker"],
    },
    "command-router": {
        "display_name": "Command Router",
        "type": "agent",
        "patterns": ["das-command-router"],
    },
    "db": {
        "display_name": "MongoDB",
        "type": "atomdb",
        "patterns": ["das-cli-mongodb"],
    },
    "redis": {
        "display_name": "Redis",
        "type": "atomdb",
        "patterns": ["das-cli-redis"],
    },
    "morkdb": {
        "display_name": "MorkDB",
        "type": "atomdb",
        "patterns": ["das-morkdb", "das-cli-morkdb"],
    },
    "adapterdb": {
        "display_name": "AdapterDB",
        "type": "atomdb",
        "patterns": ["das-adapterdb"],
    },
}


def _patterns_for_key(service_key: str) -> list[str]:
    catalog = SERVICE_CATALOG.get(service_key)
    if catalog:
        return catalog["patterns"]

    for service in DASServices:
        if service.value["command"] == service_key:
            pattern = service.value["pattern"]
            if isinstance(pattern, str):
                return [pattern]
            return list(pattern)

    return [service_key]


def build_service_row(service_key: str, service: dict) -> dict:
    catalog = SERVICE_CATALOG.get(service_key, {})
    port = service.get("port")

    return {
        "key": service_key,
        "displayName": catalog.get("display_name", service_key),
        "type": catalog.get("type", "service"),
        "host": service.get("host", ""),
        "port": port if port else None,
        "patterns": _patterns_for_key(service_key),
    }
