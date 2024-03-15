import click
from sys import exit
from commands.server import server
from commands.faas import faas
from commands.config import config
from commands.metta import metta
from commands.example import example
from commands.logs import logs
from config import Secret, SECRETS_PATH, USER_DAS_PATH


@click.group()
@click.pass_context
def das_cli(ctx):
    ctx.ensure_object(dict)

    try:
        ctx.obj["config"] = Secret()
    except PermissionError:
        click.secho(
            f"\nIt seems that you don't have the required permissions to write to {SECRETS_PATH}.\n\nTo resolve this, please make sure you are the owner of the file by running: `sudo chown $USER:$USER {USER_DAS_PATH} -R`, and then grant the necessary permissions using: `sudo chmod 770 {USER_DAS_PATH} -R`\n",
            fg="red",
        )
        exit(1)


das_cli.add_command(config)
das_cli.add_command(server)
das_cli.add_command(faas)
das_cli.add_command(metta)
das_cli.add_command(example)
das_cli.add_command(logs)

if __name__ == "__main__":
    das_cli()
