from common import Module
from .db_cli import DbCli


class DbModule(Module):
    _instance = DbCli
    _dependecy_injection = []
