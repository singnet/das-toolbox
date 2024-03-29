import click
from sys import exit
from services import RedisContainerService, MongoContainerService
from services import OpenFaaSContainerService
from exceptions import DockerDaemonException, DockerException


@click.group(help="Manage container logs.")
@click.pass_context
def logs(ctx):
    global config

    config = ctx.obj["config"]


@logs.command(help="Display logs for OpenFaaS services.")
def faas():
    openfaas_container_name = config.get("openfaas.container_name")
    mongodb_container_name = config.get("mongodb.container_name")
    redis_container_name = config.get("redis.container_name")

    try:
        openfaas_service = OpenFaaSContainerService(
            openfaas_container_name,
            redis_container_name,
            mongodb_container_name,
        )

        openfaas_service.logs()
    except DockerException as e:
        click.secho(str(e), fg="red")
        click.secho("You need to run the server with command 'server start'", fg="red")
        exit(1)
    except DockerDaemonException as e:
        click.secho(f"{str(e)}\n", fg="red")
        exit(1)


@logs.command(help="Display logs for MongoDB.")
def mongodb():
    mongodb_container_name = config.get("mongodb.container_name")

    try:
        mongodb_service = MongoContainerService(mongodb_container_name)

        mongodb_service.logs()
    except DockerException as e:
        click.secho(str(e), fg="red")
        click.secho("You need to run the server with command 'server start'", fg="red")
        exit(1)
    except DockerDaemonException as e:
        click.secho(f"{str(e)}\n", fg="red")
        exit(1)


@logs.command(help="Display logs for Redis.")
def redis():
    redis_container_name = config.get("redis.container_name")

    try:
        redis_service = RedisContainerService(redis_container_name)

        redis_service.logs()
    except DockerException as e:
        click.secho(str(e), fg="red")
        click.secho("You need to run the server with command 'server start'", fg="red")
        exit(1)
    except DockerDaemonException as e:
        click.secho(f"{str(e)}\n", fg="red")
        exit(1)
