from common import Module
from .faas_cli import FaaSCli


class FaaSModule(Module):
    _instance = FaaSCli
    _dependecy_injection = []
