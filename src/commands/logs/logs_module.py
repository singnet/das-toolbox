from common import Module

from .logs_cli import LogsCli


class LogsModule(Module):
    _instance = LogsCli
    _dependecy_injection = []
