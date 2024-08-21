from common import Module

from .metta_cli import MettaCli


class MettaModule(Module):
    _instance = MettaCli
    _dependecy_injection = []
