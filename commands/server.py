import click
from services.container import ContainerService

container_service = ContainerService()


@click.group()
def server():
    pass


@server.command()
@click.option(
    "--redis-port",
    help="Specify the port for the Redis server. Default is 6379.",
    required=False,
    default=6379,
    type=int,
)
@click.option(
    "--mongodb-port",
    help="Specify the port for the MongoDB server. Default is 27017.",
    required=False,
    default=27017,
    type=int,
)
@click.option(
    "--mongodb-username",
    help="Specify the username for MongoDB authentication.",
    required=True,
)
@click.option(
    "--mongodb-password",
    help="Specify the password for MongoDB authentication.",
    required=True,
)
def start(redis_port, mongodb_port, mongodb_username, mongodb_password):
    container_service.setup_redis(redis_port)
    container_service.setup_mongodb(
        mongodb_port,
        mongodb_username,
        mongodb_password,
    )


@server.command()
def stop():
    container_service.prune()
