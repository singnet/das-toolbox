from fastapi.concurrency import run_in_threadpool

from shared.internal.web_configuration import WebConfiguration
from shared.utils.service_inventory import build_initial_state


class DashboardServices:

    def __init__(self, web_config: WebConfiguration):
        self.web_config = web_config

    async def fetch_initial_state(self) -> dict:
        await run_in_threadpool(self.web_config.load_config_dictionary)
        return build_initial_state(self.web_config)
