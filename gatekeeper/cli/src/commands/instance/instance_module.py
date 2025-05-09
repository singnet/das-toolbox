from common import Module
from .instance_cli import InstanceCli

class InstanceModule(Module):
    _instance = InstanceCli
    _dependecy_injection = []

