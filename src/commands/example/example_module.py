from common import Module
from .example_cli import ExampleCli, ExampleFaaS, ExampleLocal
from common import get_script_name


class ExampleModule(Module):
    _instance = ExampleCli
    _dependecy_injection = [
        (ExampleFaaS, lambda: ExampleFaaS(get_script_name())),
        (ExampleLocal, lambda: ExampleLocal(get_script_name())),
    ]
