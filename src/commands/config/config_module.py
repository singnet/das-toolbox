from common import Module

from .config_cli import ConfigCli


class ConfigModule(Module):
    _instance = ConfigCli
    _dependecy_injection = []
