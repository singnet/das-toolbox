from typing import List

from common import Module

from .gkctl import GkCtl


class GkCtlModule(Module):
    _instance = GkCtl
    _dependecy_injection: List = []
