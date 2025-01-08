from typing import List

from injector import Binder
from injector import Module as InjectorModule


class Module(InjectorModule):
    # list<[tuple<(interface, instance)>]>
    _dependecy_injection: List = []
    _instance = None

    def __init__(self) -> None:
        super().__init__()

    def configure(self, binder: Binder) -> None:
        for module in self._dependecy_injection:
            binder.bind(
                interface=module[0],
                to=module[1],
            )

    def get_instance(self):
        return self._instance
