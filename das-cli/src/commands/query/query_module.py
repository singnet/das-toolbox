import os

from common import Module
from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH

from ..query_agent.query_client import CommandRouterQueryClient
from .query_cli import QueryCli, QueryRun, Settings


class QueryModule(Module):
    _instance = QueryCli

    def __init__(self) -> None:
        super().__init__()

        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))
        self._query_client = CommandRouterQueryClient(settings=self._settings)

        self._dependency_list = [
            (
                Settings,
                self._settings,
            ),
            (
                CommandRouterQueryClient,
                self._query_client,
            ),
            (
                QueryRun,
                QueryRun,
            ),
        ]