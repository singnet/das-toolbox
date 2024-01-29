import click
import docker

docker_client = docker.from_env()


@click.group()
def server():
    pass


@server.command()
@click.option("--redis-port", help="", required=False, default=6379)
@click.option("--mongodb-port", help="", required=False, default=27017)
def start(redis_port, mongodb_port):
    redis_container = docker_client.containers.run(
        "redis:7.2.3-alpine",
        detach=True,
        ports={
            "6379/tcp": redis_port,
        },
    )
    mongodb_container = docker_client.containers.run(
        "mongo:6.0.13-jammy",
        detach=True,
        ports={
            "27017/tcp": mongodb_port,
        },
    )

    print(redis_container)
    print(mongodb_container)


@server.command()
def stop():
    containers = docker_client.containers.list()

    for container in containers:
        print(f"Parando container: {container.id}")
        container.stop()
