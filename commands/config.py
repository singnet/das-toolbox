import click
from services.config import ConfigService
from utils import format_as_table


@click.group()
def config():
    global config_service

    config_service = ConfigService()
    config_service.load()


@config.command()
def set():
    redis_port = click.prompt(
        "Enter Redis port",
        default=config_service.get("redis.port", 6379),
        type=int,
    )
    config_service.set("redis.port", redis_port)

    mongodb_port = click.prompt(
        "Enter MongoDB port",
        default=config_service.get("mongodb.port", 27017),
        type=int,
    )
    mongodb_username = click.prompt(
        "Enter MongoDB username",
    )
    mongodb_password = click.prompt(
        "Enter MongoDB password",
        hide_input=True,
    )

    config_service.set("mongodb.port", mongodb_port)
    config_service.set("mongodb.username", mongodb_username)
    config_service.set("mongodb.password", mongodb_password)

    config_service.save()
    click.echo(f"Configuration saved to {config_service.get_config_path()}")


@config.command()
def list():
    config_dict = config_service.get_config()

    if len(config_dict.keys()) < 1:
        click.echo(
            f"Config not found in {config_service.get_config_path()}. You can run the command `config set` to create a configuration file."
        )
        return

    config_table = format_as_table(config_dict)

    click.echo(config_table)