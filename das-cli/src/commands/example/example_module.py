from common import Module, get_script_name

from .example_cli import ExampleCli, ExampleLocal


class ExampleModule(Module):
    _instance = ExampleCli
    _dependency_list = [
        (ExampleLocal, lambda: ExampleLocal(get_script_name())),
    ]
