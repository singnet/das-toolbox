import click
from docker.errors import NullResource
from config import Secret
from services import RedisContainerService, MongoContainerService
from services import OpenFaaSContainerService


@click.group(help="Manage container logs.")
def logs():
    global config

    config = Secret()

    if not config.exists():
        click.echo(
            "The configuration file does not exist. Please initialize the configuration file first by running the command config set."
        )
        exit(1)


@logs.command(help="Display logs for OpenFaaS services.")
def faas():
    openfaas_container_name = config.get("openfaas.container_name")
    mongodb_container_name = config.get("mongodb.container_name")
    redis_container_name = config.get("redis.container_name")

    openfaas_service = OpenFaaSContainerService(
        openfaas_container_name,
        redis_container_name,
        mongodb_container_name,
    )

    try:
        container_id = openfaas_service.get_container().get_id()
        openfaas_service.logs(container_id)
    except NullResource:
        click.echo("You need to run the server with command 'faas start'")
        exit(1)


@logs.command(help="Display logs for MongoDB.")
def mongodb():
    mongodb_container_name = config.get("mongodb.container_name")

    mongodb_service = MongoContainerService(mongodb_container_name)

    try:
        container_id = mongodb_service.get_container().get_id()
        mongodb_service.logs(container_id)
    except NullResource:
        click.echo("You need to run the server with command 'server start'")
        exit(1)


@logs.command(help="Display logs for Redis.")
def redis():
    redis_container_name = config.get("redis.container_name")

    redis_service = RedisContainerService(redis_container_name)

    try:
        container_id = redis_service.get_container().get_id()
        redis_service.logs(container_id)
    except NullResource:
        click.echo("You need to run the server with command 'server start'")
        exit(1)
