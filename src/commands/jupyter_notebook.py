import click
from services.jupyter_notebook_container_service import JupyterNotebookContainerService
from exceptions import (
    ContainerAlreadyRunningException,
    DockerException,
    DockerDaemonException,
    NotFound,
)


@click.group()
@click.pass_context
def jupyter_notebook(ctx):
    """
    Manage Jupyter Notebook.

    'das-cli jupyter-notebook' allows you to manage Jupyter Notebook environments providing commands to start, stop, and restart Jupyter Notebook servers, enabling you to interactively create, edit, and run Python notebooks.
    """
    global config

    config = ctx.obj["config"]


@jupyter_notebook.command()
def restart():
    """
    Restart Jupyter Notebook.

    'das-cli jupyter-notebook restart' restarts a Jupyter Notebook environment.
    This command stops the currently running Jupyter server, then starts a new instance of the server, effectively restarting the environment.

    .SH EXAMPLES

    Restart a Jupyter Notebook environment.

    $ das-cli jupyter-notebook restart
    """
    ctx = click.Context(restart)
    ctx.invoke(stop)
    ctx.invoke(start)


@jupyter_notebook.command()
def start():
    """
    Start a Jupyter Notebook.

    'das-cli jupyter-notebook start' starts a Jupyter Notebook environment.
    This command launches a Jupyter server on your local machine, allowing you to create, edit, and run Python notebooks interactively in your web browser.
    After starting the Jupyter Notebook environment, the command will display the port in your terminal.
    You can access the Jupyter Notebook by navigating to localhost using the displayed port number in your web browser.
    There is no token or password required for access.

    .SH EXAMPLES

    Start a Jupyter Notebook environment.

    $ das-cli jupyter-notebook start
    """

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


@jupyter_notebook.command()
def stop():
    """
    Stop a Jupyter Notebook.

    'das-cli jupyter-notebook stop' stops a running Jupyter Notebook environment.

    .SH EXAMPLES

    Stop a running Jupyter Notebook environment.

    $ das-cli jupyter-notebook stop
    """
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
