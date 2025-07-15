from injector import inject

from common import Command, CommandGroup, CommandOption, Settings, StdoutSeverity
from common.docker.exceptions import (
    DockerContainerDuplicateError,
    DockerContainerNotFoundError,
    DockerError,
)
from common.prompt_types import AbsolutePath

from .jupyter_notebook_container_manager import JupyterNotebookContainerManager


class JupyterNotebookStart(Command):
    name = "start"

    short_help = "Start a Jupyter Notebook."

    help = """
NAME

    jupyter-notebook start - Start a Jupyter Notebook environment

SYNOPSIS

    das-cli jupyter-notebook start [--working-dir <directory>]

DESCRIPTION

    Starts a Jupyter Notebook environment by launching a Jupyter server locally.
    This allows you to create, edit, and run Python notebooks interactively via your web browser.
    After starting, the command displays the port number where the server is listening.
    Access the notebook by navigating to 'localhost:<port>' in your browser.
    No token or password is required to access the notebook.

OPTIONS

    --working-dir, -w
        Optional. Specify a custom working directory to bind to the Jupyter Notebook container.

EXAMPLES

    Start a Jupyter Notebook environment:

        das-cli jupyter-notebook start

    Start a Jupyter Notebook with a custom working directory:

        das-cli jupyter-notebook start --working-dir /path/to/working/directory
"""

    params = [
        CommandOption(
            ["--working-dir", "-w"],
            help="The working directory to bind to the Jupyter Notebook container.",
            required=False,
            default=None,
            type=AbsolutePath(
                file_okay=False,
                dir_okay=True,
                exists=True,
                writable=True,
                readable=True,
            ),
        )
    ]

    @inject
    def __init__(
        self,
        settings: Settings,
        jupyter_notebook_container_manager: JupyterNotebookContainerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._jupyter_notebook_container_manager = jupyter_notebook_container_manager

    def run(self, working_dir: str | None = None):
        self._settings.raise_on_missing_file()
        self._settings.raise_on_schema_mismatch()

        self.stdout("Starting Jupyter Notebook...")

        jupyter_notebook_port = self._settings.get("services.jupyter_notebook.port")

        try:
            self._jupyter_notebook_container_manager.start_container(
                jupyter_notebook_port,
                working_dir,
            )
            self.stdout(
                f"Jupyter Notebook started on port {jupyter_notebook_port}",
                severity=StdoutSeverity.SUCCESS,
            )
        except DockerContainerDuplicateError:
            self.stdout(
                f"Jupyter Notebook is already running. It's listening on port {jupyter_notebook_port}",
                severity=StdoutSeverity.WARNING,
            )
        except DockerError:
            raise DockerError(
                f"\nError occurred while trying to start Jupyter Notebook on port {jupyter_notebook_port}\n"
            )


class JupyterNotebookStop(Command):
    name = "stop"

    short_help = "Stop a Jupyter Notebook."

    help = """
NAME

    jupyter-notebook stop - Stop a running Jupyter Notebook environment

SYNOPSIS

    das-cli jupyter-notebook stop

DESCRIPTION

    Stops the currently running Jupyter Notebook environment.

EXAMPLES

    Stop a running Jupyter Notebook environment:

        das-cli jupyter-notebook stop
"""

    @inject
    def __init__(
        self,
        settings: Settings,
        jupyter_notebook_container_manager: JupyterNotebookContainerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._jupyter_notebook_container_manager = jupyter_notebook_container_manager

    def run(self):
        self._settings.raise_on_missing_file()
        self._settings.raise_on_schema_mismatch()

        self.stdout("Stopping jupyter notebook...")

        try:
            self._jupyter_notebook_container_manager.stop()
            self.stdout(
                "Jupyter Notebook service stopped",
                severity=StdoutSeverity.SUCCESS,
            )
        except DockerContainerNotFoundError:
            container_name = self._jupyter_notebook_container_manager.get_container().name
            self.stdout(
                f"The Jupyter Notebook service named {container_name} is already stopped.",
                severity=StdoutSeverity.WARNING,
            )


class JupyterNotebookRestart(Command):
    name = "restart"

    short_help = "Restart Jupyter Notebook."

    help = """
NAME

    jupyter-notebook restart - Restart a Jupyter Notebook environment

SYNOPSIS

    das-cli jupyter-notebook restart [--working-dir <directory>]

DESCRIPTION

    Restarts the Jupyter Notebook environment by stopping the current instance and starting a new one.
    Useful to refresh the environment or apply configuration changes.

OPTIONS

    --working-dir, -w
        Optional. Specify a custom working directory to bind to the Jupyter Notebook container.

EXAMPLES

    Restart the Jupyter Notebook environment:

        das-cli jupyter-notebook restart

    Restart with a custom working directory:

        das-cli jupyter-notebook restart --working-dir /path/to/working/directory
"""

    params = [
        CommandOption(
            ["--working-dir", "-w"],
            help="The working directory to bind to the Jupyter Notebook container.",
            required=False,
            default=None,
            type=AbsolutePath(
                file_okay=False,
                dir_okay=True,
                exists=True,
                writable=True,
                readable=True,
            ),
        )
    ]

    @inject
    def __init__(
        self,
        jupyter_notebook_start: JupyterNotebookStart,
        jupyter_notebook_stop: JupyterNotebookStop,
    ) -> None:
        super().__init__()
        self._jupyter_notebook_start = jupyter_notebook_start
        self._jupyter_notebook_stop = jupyter_notebook_stop

    def run(self, working_dir: str | None = None):
        self._jupyter_notebook_stop.run()
        self._jupyter_notebook_start.run(working_dir)


class JupyterNotebookCli(CommandGroup):
    name = "jupyter-notebook"

    short_help = "Manage Jupyter Notebook."

    help = """
NAME

    jupyter-notebook - Manage Jupyter Notebook environments

SYNOPSIS

    das-cli jupyter-notebook <command> [options]

DESCRIPTION

    Provides commands to start, stop, and restart Jupyter Notebook environments.
    Enables interactive creation, editing, and execution of Python notebooks.

COMMANDS

    start       Start a Jupyter Notebook environment.
    stop        Stop a running Jupyter Notebook environment.
    restart     Restart the Jupyter Notebook environment.

EXAMPLES

    Start the notebook:

        das-cli jupyter-notebook start

    Stop the notebook:

        das-cli jupyter-notebook stop

    Restart the notebook:

        das-cli jupyter-notebook restart
"""

    @inject
    def __init__(
        self,
        jupyter_notebook_start: JupyterNotebookStart,
        jupyter_notebook_stop: JupyterNotebookStop,
        jupyter_notebook_restart: JupyterNotebookRestart,
    ) -> None:
        super().__init__()
        self.add_commands(
            [
                jupyter_notebook_start,
                jupyter_notebook_stop,
                jupyter_notebook_restart,
            ]
        )
