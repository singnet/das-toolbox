from common.docker.docker_manager import DockerManager
from common.settings import Settings
from common.utils import extract_service_name
import re


class SystemContainersManager(DockerManager):
    def __init__(self, settings: Settings, exec_context: str | None = None) -> None:
        super().__init__(exec_context)

        self._settings = settings

    def _get_services(self) -> list:
        services = []
        services_settings = self._settings.get("services", {})

        for service_settings in services_settings.values():
            service_name = service_settings.get("container_name")
            if service_name:
                services.append(service_name)

        return services

    def _list_service_containers(self, all: bool = False) -> list:
        services = self._get_services()
        return self.get_docker_client().containers.list(
            all=all, filters={"name": services}
        )

    def get_services_status(self) -> dict:
        expected_services = self._get_services()
        containers = self._list_service_containers(all=True)

        status = {}

        for container in containers:
            service_name = extract_service_name(container.name)
            version = self._extract_version(container)
            port_range = self._extract_port_range(container)
            port = container.name.split("-")[-1] or None

            status[service_name] = {
                "status": container.status,
                "version": version,
                "port": port,
                "port_range": port_range,
            }

        for service in expected_services:
            service_name = extract_service_name(service)
            if service_name not in status:
                status[service_name] = {
                    "status": "not running",
                    "version": ("unknown",),
                    "port": None,
                    "port_range": None,
                }

        return status


    def _extract_version(self, container) -> tuple:
        image_tags = getattr(container.image, "tags", [])
        if image_tags:
            tag = image_tags[0].split(":")
            version_str = tag[1] if len(tag) > 1 else "latest"
            match = re.search(r"v?(\d+\.\d+\.\d+)", version_str)
            return match.groups() if match else (version_str,)
        return ("unknown",)

    def _extract_port_range(self, container) -> str | None:
        args = (
            container.attrs.get("Args")
            or container.attrs.get("Config", {}).get("Cmd")
            or []
        )

        if not isinstance(args, list):
            return None

        port_range_pattern = re.compile(r"^\d{2,5}:\d{2,5}$")

        for arg in args:
            if isinstance(arg, str) and port_range_pattern.match(arg):
                return arg

        return None
