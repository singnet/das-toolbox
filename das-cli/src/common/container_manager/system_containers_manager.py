import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from dateutil.parser import isoparse
from docker.models.containers import Container

from common.docker.docker_manager import DockerManager
from common.settings import Settings


class SystemContainersManager(DockerManager):

    def __init__(
        self,
        settings: Settings,
        exec_context: str | None = None,
    ) -> None:
        super().__init__(exec_context)
        self._settings = settings

    def _list_service_containers(self) -> list[Container]:
        return self.get_docker_client().containers.list(filters={"name": "das"})

    def get_services_status(self) -> dict:

        containers = self._list_service_containers()
        services = {}

        stats = self.map_services_thread(self._safe_get_container_stats, containers)

        for stat in stats:
            services[stat["container_name"]] = stat

        return services

    def _safe_get_container_stats(self, container: Container) -> dict:
        try:
            container_stats = container.stats(stream=False)
            cpu_memory_info = self._parse_container_stats(container_stats)

            container_name = container.name
            image = self._extract_image(container)
            port = self._extract_port(container)
            age = self._calculate_uptime(container)
            status = container.status
            service_health = self._extract_health(container)

            return {
                "container_name": container_name,
                "image": image,
                "port": port,
                "age": age,
                "cpu_percent": cpu_memory_info.get("cpu_percent", 0),
                "memory_mb": cpu_memory_info.get("memory_mb", 0),
                "status": status,
                "service_health": service_health,
            }

        except Exception:
            return {
                "cpu_percent": 0,
                "memory_mb": 0,
            }

    def _extract_image(self, container: Container) -> str:
        tags = getattr(container.image, "tags", [])

        if tags:
            return tags[0]

        return "-"

    def _extract_port(self, container: Container) -> str:

        attrs = container.attrs

        # Ports via NetworkSettings
        ports = attrs.get("NetworkSettings", {}).get("Ports", {})

        if ports:
            for _, mappings in ports.items():
                if mappings and isinstance(mappings, list):
                    host_port = mappings[0].get("HostPort")

                    if host_port:
                        return host_port

        # Fallback para Args
        args = attrs.get("Args", [])

        for i, arg in enumerate(args):

            if "--endpoint" in arg and ":" in arg:
                return arg.split(":")[-1]

            if arg == "--port" and i + 1 < len(args):
                return args[i + 1]

        # Fallback para nome do container
        name_match = re.search(r"-(\d+)$", container.name)

        if name_match:
            return name_match.group(1)

        return "-"

    def _extract_health(self, container: Container) -> str:

        attrs = container.attrs

        health = attrs.get("State", {}).get("Health", {}).get("Status")

        return health or "-"

    def _calculate_uptime(self, container: Container) -> str:

        attrs = container.attrs

        started_at = attrs.get("State", {}).get("StartedAt")

        if not started_at:
            return "-"

        started = isoparse(started_at)

        now = datetime.now(timezone.utc)

        elapsed = now - started

        days = elapsed.days
        hours = elapsed.seconds // 3600
        minutes = (elapsed.seconds % 3600) // 60

        if days > 0:
            return f"{days}d {hours}h"

        if hours > 0:
            return f"{hours}h {minutes}m"

        return f"{minutes}m"

    def _parse_container_stats(self, stats: dict) -> dict:

        cpu_percent = self._calculate_cpu_percent(stats)

        memory_usage = stats.get("memory_stats", {}).get("usage", 0)
        
        memory_mb = round(
            memory_usage / (1024 ** 3),
            2,
        )

        return {
            "cpu_percent": round(cpu_percent, 2),
            "memory_mb": memory_mb,
        }

    def _calculate_cpu_percent(self, stats: dict) -> float:

        cpu_stats = stats.get("cpu_stats", {})
        precpu_stats = stats.get("precpu_stats", {})

        cpu_total = cpu_stats.get("cpu_usage", {}).get("total_usage", 0)

        prev_cpu_total = precpu_stats.get("cpu_usage", {}).get("total_usage", 0)

        system_cpu = cpu_stats.get(
            "system_cpu_usage",
            0,
        )

        prev_system_cpu = precpu_stats.get(
            "system_cpu_usage",
            0,
        )

        cpu_delta = cpu_total - prev_cpu_total
        system_delta = system_cpu - prev_system_cpu

        if cpu_delta > 0 and system_delta > 0:
            return (cpu_delta / system_delta) * 100.0

        return 0.0

    def map_services_thread(self, fetch_function, containers: Container):

        with ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(fetch_function, containers)

        return results
