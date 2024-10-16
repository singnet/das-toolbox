from common import Module

from .db_adapter_cli import DbAdapterCli


class DbAdapterModule(Module):
    _instance = DbAdapterCli
    _dependecy_injection = []
