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

OFFLINE_EMPTY = "-"

SERVICE_CATALOG: dict[str, dict] = {
    "query-engine": {"display_name": "Query Agent", "type": "agent"},
    "link-creation-agent": {"display_name": "Link Creation Agent", "type": "agent"},
    "inference-agent": {"display_name": "Inference Agent", "type": "agent"},
    "evolution-agent": {"display_name": "Evolution Agent", "type": "agent"},
    "attention-broker": {"display_name": "Attention Broker", "type": "broker"},
    "context-broker": {"display_name": "Context Broker", "type": "broker"},
    "atomdb-broker": {"display_name": "AtomDB Broker", "type": "broker"},
    "command-router": {"display_name": "Command Router", "type": "agent"},
    "db": {"display_name": "MongoDB", "type": "atomdb"},
    "redis": {"display_name": "Redis", "type": "atomdb"},
    "morkdb": {"display_name": "MorkDB", "type": "atomdb"},
    "adapterdb": {"display_name": "AdapterDB", "type": "atomdb"},
}


def build_service_row(service_key: str, service: dict) -> dict:
    catalog = SERVICE_CATALOG.get(service_key, {})
    port = service.get("port")

    return {
        "service_key": service_key,
        "display_name": catalog.get("display_name", service_key),
        "type": catalog.get("type", "service"),
        "host": service.get("host", ""),
        "port": port if port else OFFLINE_EMPTY,
        "service_command_label": service_key,
        "container_name": None,
        "image": OFFLINE_EMPTY,
        "age": OFFLINE_EMPTY,
        "cpu_percent": None,
        "memory_mb": None,
        "service_health": OFFLINE_EMPTY,
        "status": "offline",
        "is_running": False,
    }


def build_initial_state(web_config) -> dict:
    hosts = web_config.map_dashboard_hosts()
    service_server_map: dict[str, list[str]] = {}

    for host_entry in hosts:
        ip = host_entry["ip"]
        for service in host_entry["services"]:
            service_key = service["service_key"]
            servers = service_server_map.setdefault(service_key, [])
            if ip not in servers:
                servers.append(ip)

    return {"hosts": hosts, "serviceServerMap": service_server_map}
