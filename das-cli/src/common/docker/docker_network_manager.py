import docker

from .docker_manager import DockerManager
from common.utils import log_exception


class DockerNetworkManager(DockerManager):
    def create_network(
        self,
        name: str,
        driver: str = "bridge",
        subnet: str = None,
    ):
        ipam_config = None
        if subnet:
            ipam_pool = docker.types.IPAMPool(subnet=subnet)
            ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])

        network = self._get_client().networks.create(
            name=name, driver=driver, ipam=ipam_config
        )
        return network

    def list_networks(self):
        return [net.name for net in self._get_client().networks.list()]

    def remove_network(self, name: str):
        network = self._get_client().networks.get(name)
        network.remove()

    def get_network_by_name(self, name: str):
        networks = self._get_client().networks.list(names=[name])
        return networks[0] if networks else None


def init_network():
    from common.docker.docker_network_manager import DockerNetworkManager
    from settings.config import SERVICES_NETWORK_NAME

    try:
        network_manager = DockerNetworkManager()
        network = network_manager.get_network_by_name(SERVICES_NETWORK_NAME)
        if network is None:
            network_manager.create_network(name=SERVICES_NETWORK_NAME)
    except Exception as e:
        log_exception(e)
        exit(1)