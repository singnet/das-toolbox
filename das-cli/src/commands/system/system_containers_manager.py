from common.docker.docker_manager import DockerManager
from common.settings import Settings
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
    return self.get_docker_client().containers.list(all=all, filters={"name": services})

  def get_services_status(self) -> dict:
    containers = self._list_service_containers(all=True)
    status = {}
    for container in containers:
        version = self._extract_version(container)
        formatted_ports = self._format_ports(container)
        status[container.name] = {
            "status": container.status,
            "version": version,
            "ports": formatted_ports,
        }
    return status

  def _extract_version(self, container) -> tuple:
    image_tags = getattr(container.image, 'tags', [])
    if image_tags:
        tag = image_tags[0].split(":")
        version_str = tag[1] if len(tag) > 1 else "latest"
        match = re.search(r"v?(\d+\.\d+\.\d+)", version_str)
        return match.groups() if match else (version_str,)
    return ("unknown",)

  def _format_ports(self, container) -> dict:
    ports = container.attrs.get("NetworkSettings", {}).get("Ports", {})
    formatted = {}
    for port, mappings in ports.items():
        if mappings:
            formatted[port] = [m.get("HostPort") for m in mappings if m.get("HostPort")]
        else:
            formatted[port] = []
    return formatted
