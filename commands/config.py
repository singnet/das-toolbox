import click
from config import Config
from utils import format_as_table


@click.group(help="Manage configuration settings.")
def config():
    """
    This command group allows you to manage configuration settings.
    """

    global config_service

    config_service = Config()


@config.command(help="Set Redis and MongoDB configuration settings.")
def set():
    """
    Set Redis and MongoDB configuration settings.
    """

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
        default=config_service.get("mongodb.username", "admin"),
    )
    mongodb_password = click.prompt(
        "Enter MongoDB password",
        hide_input=True,
        default=config_service.get("mongodb.password", "admin"),
    )

    config_service.set("mongodb.port", mongodb_port)
    config_service.set("mongodb.username", mongodb_username)
    config_service.set("mongodb.password", mongodb_password)

    config_service.save()
    click.echo(f"Configuration file saved to {config_service.get_path()}")


@config.command(help="Display the current configuration settings.")
def list():
    """
    Display the current configuration settings.
    """

    config_dict = config_service.get_content()

    if len(config_dict.keys()) < 1:
        click.echo(
            f"Configuration file not found in {config_service.get_path()}. You can run the command `config set` to create a configuration file."
        )
        return

    config_table = format_as_table(config_dict)

    click.echo(config_table)
