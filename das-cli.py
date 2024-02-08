import click
from commands.server import server
from commands.faas import faas
from commands.config import config
from commands.metta import metta
from commands.example import example


@click.group()
def hyperon_das():
    pass


hyperon_das.add_command(config)
hyperon_das.add_command(server)
hyperon_das.add_command(faas)
hyperon_das.add_command(metta)
hyperon_das.add_command(example)

if __name__ == "__main__":
    hyperon_das()