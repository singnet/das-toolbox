from common import Module, APIClient
from .instance_cli import InstanceCli
from .instance_service import InstanceService

class InstanceModule(Module):
    _instance = InstanceCli

    def __init__(self):
        super().__init__()
        self._dependecy_injection = [
            (
                InstanceService,
                self._instance_service_factory,
            ),
        ]


    def _instance_service_factory(self):
        api_client = APIClient("http://127.0.0.1:5000")

        return InstanceService(api_client)


