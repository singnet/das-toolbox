from common import Module
from .port_cli import PortCli

class PortModule(Module):
    _instance = PortCli
    _dependecy_injection = []

