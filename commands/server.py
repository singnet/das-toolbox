import click
from services.environment import EnvironmentService

environment_service = EnvironmentService()


@click.group()
def server():
    pass


@server.command()
@click.option("--redis-port", help="", required=False, default=6379)
@click.option("--mongodb-port", help="", required=False, default=27017)
def start(redis_port, mongodb_port):
    environment_service.setup_redis(redis_port)
    environment_service.setup_mongodb(mongodb_port)


@server.command()
def stop():
    environment_service.shutdown()
