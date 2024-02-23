import click
from config import Secret
from utils import table_parser


@click.group(help="Manage configuration settings.")
def config():
    """
    This command group allows you to manage configuration settings.
    """

    global config_service

    config_service = Secret()


@config.command(help="Set Redis and MongoDB configuration settings.")
def set():
    """
    Set Redis and MongoDB configuration settings.
    """

    redis_container_name = click.prompt(
        "Enter a name for the Redis container",
        default=config_service.get("redis.container_name", "das-cli-redis"),
        type=str,
    )
    config_service.set("redis.container_name", redis_container_name)

    redis_port = click.prompt(
        "Enter Redis port",
        default=config_service.get("redis.port", 6379),
        type=int,
    )
    config_service.set("redis.port", redis_port)

    mongodb_container_name = click.prompt(
        "Enter a name for the MongoDB container",
        default=config_service.get("mongodb.container_name", "das-cli-mongodb"),
        type=str,
    )
    config_service.set("mongodb.container_name", mongodb_container_name)

    mongodb_port = click.prompt(
        "Enter MongoDB port",
        default=config_service.get("mongodb.port", 27017),
        type=int,
    )
    config_service.set("mongodb.port", mongodb_port)
    mongodb_username = click.prompt(
        "Enter MongoDB username",
        default=config_service.get("mongodb.username", "admin"),
    )
    config_service.set("mongodb.username", mongodb_username)
    mongodb_password = click.prompt(
        "Enter MongoDB password",
        hide_input=True,
        default=config_service.get("mongodb.password", "admin"),
    )
    config_service.set("mongodb.password", mongodb_password)

    canonical_load_container_name = click.prompt(
        "Enter a name for the Canonical Load container",
        default=config_service.get(
            "canonical_load.container_name", "das-cli-canonical-load"
        ),
        type=str,
    )
    config_service.set("canonical_load.container_name", canonical_load_container_name)

    openfaas_container_name = click.prompt(
        "Enter a name for the OpenFaaS container",
        default=config_service.get("openfaas.container_name", "das-cli-openfaas"),
        type=str,
    )
    config_service.set("openfaas.container_name", openfaas_container_name)

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

    config_table = table_parser(config_dict)

    click.echo(config_table)
