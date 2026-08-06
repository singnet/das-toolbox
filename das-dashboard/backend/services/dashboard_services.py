from fastapi.concurrency import run_in_threadpool

from shared.internal.web_configuration import WebConfiguration


class DashboardServices:

    def __init__(self, web_config: WebConfiguration):
        self.web_config = web_config

    def build_initial_state(self) -> dict:
        dashboard_hosts = self.web_config.map_dashboard_hosts()
        service_server_map: dict[str, list[str]] = {}
        hosts = []

        for host_entry in dashboard_hosts:
            ip = host_entry["ip"]
            services = []

            for row in host_entry["services"]:
                service_key = row["key"]
                service_server_map.setdefault(service_key, [])

                if ip not in service_server_map[service_key]:
                    service_server_map[service_key].append(ip)

                services.append({
                    "service_key": service_key,
                    "display_name": row["displayName"],
                    "type": row.get("type", "service"),
                    "orchestration_group": row.get("orchestrationGroup"),
                    "host": row.get("host", ""),
                    "port": row.get("port"),
                    "status": "offline",
                    "is_running": False,
                })

            hosts.append({"ip": ip, "services": services})

        return {
            "hosts": hosts,
            "serviceServerMap": service_server_map,
        }

    async def fetch_initial_state(self) -> dict:
        await run_in_threadpool(self.web_config.load_config_dictionary)
        return self.build_initial_state()
