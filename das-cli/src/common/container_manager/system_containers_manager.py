from datetime import datetime, timezone
from dateutil.parser import isoparse
from common.docker.docker_manager import DockerManager
from common.settings import Settings
import re

class SystemContainersManager(DockerManager):

    def __init__(self, settings: Settings, exec_context: str | None = None) -> None:

        super().__init__(exec_context)
        self._settings = settings

    def _list_service_containers(self) -> list:
        return self.get_docker_client().containers.list(filters={"name": "das"})

    def get_services_status(self) -> dict:
        containers = self._list_service_containers()
        services = {}

        for container in containers:
            stats = self._safe_get_container_stats(container)
            services[container.name] = {
                "container_name": container.name,
                "image": self._extract_image(container),
                "port": self._extract_port(container),
                "age": self._calculate_uptime(container),
                "cpu_percent": stats.get("cpu_percent", 0),
                "memory_mb": stats.get("memory_mb", 0),
                "status": container.status,
                "service_health": self._extract_health(container),
            }

        return services

    def _extract_image(self, container) -> str:
        tags = getattr(container.image, "tags", [])
        if tags:
            return tags[0]
        return "-"

    def _extract_port(self, container) -> str:

        # Ports being extracted via container Network Settings
        ports = container.attrs.get("NetworkSettings", {}).get("Ports", {})
        if ports:
            for container_port, mappings in ports.items():
                if mappings and isinstance(mappings, list):
                    host_port = mappings[0].get("HostPort")
                    if host_port:
                        return host_port

        # fallback to args in case it's empty.
        args = container.attrs.get("Args", [])
        for i, arg in enumerate(args):
            if "--endpoint" in arg and ":" in arg:
                return arg.split(":")[-1]
            if arg == "--port" and i + 1 < len(args):
                return args[i+1]
        
        # fallback to container name
        name_match = re.search(r'-(\d+)$', container.name)
        if name_match:
            return name_match.group(1)
        
        return "-"

    def _extract_health(self, container) -> str:
        health = container.attrs.get("State", {}).get("Health", {}).get("Status")
        return health or "-"

    def _calculate_uptime(self, container) -> str:
        started_at = container.attrs.get("State", {}).get("StartedAt")
        if not started_at:
            return "-"
        started = isoparse(started_at)
        now = datetime.now(timezone.utc)
        timePassed = now - started
        days = timePassed.days
        hours = timePassed.seconds // 3600
        minutes = (timePassed.seconds % 3600) // 60
        if days > 0:
            return f"{days}d {hours}h"
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"

    def _safe_get_container_stats(self, container) -> dict:
        try:
            stats = container.stats(stream=False)
            return self._parse_container_stats(stats)
        except Exception:
            return {
                "cpu_percent": 0,
                "memory_mb": 0,
            }

    def _parse_container_stats(self, stats: dict) -> dict:
        cpu_percent = self._calculate_cpu_percent(stats)
        memory_usage = stats.get("memory_stats", {}).get("usage", 0)
        memory_mb = round(memory_usage / (1024 * 1024), 2)
        return {
            "cpu_percent": round(cpu_percent, 2),
            "memory_mb": memory_mb,
        }

    def _calculate_cpu_percent(self, stats: dict) -> float:
        cpu_stats = stats.get("cpu_stats", {})
        previous_cpu_stats = stats.get("precpu_stats", {})

        cpu_total = cpu_stats.get("cpu_usage", {}).get("total_usage", 0)
        previous_cpu_total = previous_cpu_stats.get("cpu_usage", {}).get("total_usage", 0)

        system_cpu = cpu_stats.get("system_cpu_usage", 0)
        previous_system_cpu = previous_cpu_stats.get("system_cpu_usage", 0)

        container_used_cpu = cpu_total - previous_cpu_total
        system_used_cpu = system_cpu - previous_system_cpu

        if system_used_cpu > 0 and container_used_cpu > 0:
            return (container_used_cpu / system_used_cpu) * 100.0 * 12
        return 0.0
