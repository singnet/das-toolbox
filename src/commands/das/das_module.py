from common import Module

from .das_cli import DasCli


class DasModule(Module):
    _instance = DasCli
    _dependecy_injection = []
