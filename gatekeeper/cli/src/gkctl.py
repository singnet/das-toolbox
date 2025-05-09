from injector import Injector

from commands.gkctl import GkCtlModule
from commands.port import PortModule

MODULES = [
    PortModule,
]


def init_module(cli, module):
    m = module()
    container = Injector([m])
    instance = container.get(m.get_instance())
    cli.add_command(instance.group)


def init_modules(cli):
    for module in MODULES:
        init_module(cli, module)


def init_cli(module):
    m = module()
    container = Injector([m])
    instance = container.get(m.get_instance())

    return instance.group


gkctl = init_cli(GkCtlModule)
init_modules(gkctl)

if __name__ == "__main__":
    gkctl()
