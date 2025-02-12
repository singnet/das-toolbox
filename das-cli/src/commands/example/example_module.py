from common import Module, get_script_name

from .example_cli import ExampleCli, ExampleFaaS, ExampleLocal


class ExampleModule(Module):
    _instance = ExampleCli
    _dependecy_injection = [
        (ExampleFaaS, lambda: ExampleFaaS(get_script_name())),
        (ExampleLocal, lambda: ExampleLocal(get_script_name())),
    ]
