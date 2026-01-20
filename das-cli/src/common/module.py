from typing import Any, List

from injector import Binder
from injector import Module as InjectorModule


class Module(InjectorModule):
    _dependency_list: List = [tuple[Any, Any]]
    _instance: Any

    def __init__(self) -> None:
        super().__init__()

    def configure(self, binder: Binder) -> None:
        for module in self._dependency_list:
            binder.bind(
                interface=module[0],
                to=module[1],
            )

    def get_instance(self):
        return self._instance
