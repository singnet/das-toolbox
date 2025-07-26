from common import Module, get_script_name

from .example_cli import ExampleCli, ExampleLocal


class ExampleModule(Module):
    _instance = ExampleCli
    _dependecy_injection = [
        (ExampleLocal, lambda: ExampleLocal(get_script_name())),
    ]
