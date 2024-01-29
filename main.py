import click
from server import server


@click.group()
def hyperon_das():
    pass


hyperon_das.add_command(server)

if __name__ == "__main__":
    hyperon_das()
