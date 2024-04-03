import click
from services.jupyter_notebook_container_service import JupyterNotebookContainerService
from exceptions import (
    ContainerAlreadyRunningException,
    DockerException,
    DockerDaemonException,
    NotFound,
)


@click.group(help="Manage Jupyter Notebook.")
@click.pass_context
def jupyter_notebook(ctx):
    global config

    config = ctx.obj["config"]


@jupyter_notebook.command(help="Restart Jupyter Notebook.")
def restart():
    ctx = click.Context(restart)
    ctx.invoke(stop)
    ctx.invoke(start)


@jupyter_notebook.command(help="Start a Jupyter Notebook.")
def start():
    click.echo("Starting Jupyter Notebook...")

    jupyter_notebook_container_name = config.get("jupyter_notebook.container_name")
    jupyter_notebook_port = config.get("jupyter_notebook.port")

    try:
        jupyter_notebook_service = JupyterNotebookContainerService(
            jupyter_notebook_container_name
        )

        jupyter_notebook_service.start_container(
            jupyter_notebook_port,
        )
        click.secho(
            f"Jupyter Notebook started on port {jupyter_notebook_port}", fg="green"
        )
    except ContainerAlreadyRunningException:
        click.secho(
            f"Jupyter Notebook is already running. It's listening on port {jupyter_notebook_port}",
            fg="yellow",
        )
    except (DockerException, DockerDaemonException) as e:
        click.secho(
            f"\nError occurred while trying to start Jupyter Notebook on port {jupyter_notebook_port}\n",
            fg="red",
        )
        click.secho(f"{str(e)}\n", fg="red")
        exit(1)


@jupyter_notebook.command(help="Stop a Jupyter Notebook.")
def stop():
    click.echo(f"Stopping jupyter notebook...")

    jupyter_notebook_container_name = config.get("jupyter_notebook.container_name")

    try:
        JupyterNotebookContainerService(jupyter_notebook_container_name).stop()
        click.secho("Jupyter Notebook service stopped", fg="green")
    except NotFound:
        click.secho(
            f"The Jupyter Notebook service named {jupyter_notebook_container_name} is already stopped.",
            fg="yellow",
        )
    except DockerException as e:
        click.secho(
            f"\nError occurred while trying to stop Jupyter Notebook\n",
            fg="red",
        )
        click.secho(f"{str(e)}\n", fg="red")
    except DockerDaemonException as e:
        click.secho(f"{str(e)}\n", fg="red")
        exit(1)
