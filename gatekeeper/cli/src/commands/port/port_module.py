from common import Module, APIClient
from .port_cli import PortCli
from .port_service import PortService

class PortModule(Module):
    _instance = PortCli

    def __init__(self):
        super().__init__()

        self._dependecy_injection = [
            (
                PortService,
                self._port_service_factory,
            ),
        ]


    def _port_service_factory(self):
        api_client = APIClient("http://127.0.0.1:5000")

        return PortService(api_client)
