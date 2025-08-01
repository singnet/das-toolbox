from injector import inject

from common import Command, CommandGroup, CommandOption, Settings, StdoutSeverity, StdoutType
from common.docker.exceptions import (
    DockerContainerDuplicateError,
    DockerContainerNotFoundError,
    DockerError,
)
from common.prompt_types import AbsolutePath

from .jupyter_notebook_agent_container_service_response import (
    JupyterNotebookContainerServiceResponse,
)
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

    def _get_container(self):
        return self._jupyter_notebook_container_manager.get_container()

    def run(self, working_dir: str | None = None):
        self._settings.raise_on_missing_file()
        self._settings.raise_on_schema_mismatch()

        self.stdout("Starting Jupyter Notebook...")

        container = self._get_container()

        try:
            self._jupyter_notebook_container_manager.start_container(working_dir)
            success_message = f"Jupyter Notebook started on port {container.port}"
            self.stdout(
                success_message,
                severity=StdoutSeverity.SUCCESS,
            )
            self.stdout(
                dict(
                    JupyterNotebookContainerServiceResponse(
                        action="start",
                        status="success",
                        message=success_message,
                        container=container,
                        extra_details={
                            "working_dir": working_dir,
                        },
                    ),
                ),
                stdout_type=StdoutType.MACHINE_READABLE,
            )
        except DockerContainerDuplicateError:
            warning_message = (
                f"Jupyter Notebook is already running. It's listening on port {container.port}"
            )
            self.stdout(
                warning_message,
                severity=StdoutSeverity.WARNING,
            )
            self.stdout(
                dict(
                    JupyterNotebookContainerServiceResponse(
                        action="start",
                        status="already_running",
                        message=warning_message,
                        container=container,
                        extra_details={
                            "working_dir": working_dir,
                        },
                    ),
                ),
                stdout_type=StdoutType.MACHINE_READABLE,
            )
        except DockerError:
            raise DockerError(
                f"\nError occurred while trying to start Jupyter Notebook on port {container.port}\n"
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

    def _get_container(self):
        return self._jupyter_notebook_container_manager.get_container()

    def run(self):
        self._settings.raise_on_missing_file()
        self._settings.raise_on_schema_mismatch()

        container = self._get_container()

        self.stdout("Stopping jupyter notebook...")

        try:
            self._jupyter_notebook_container_manager.stop()

            success_message = "Jupyter Notebook service stopped"
            self.stdout(
                success_message,
                severity=StdoutSeverity.SUCCESS,
            )

            self.stdout(
                dict(
                    JupyterNotebookContainerServiceResponse(
                        action="stop",
                        status="success",
                        message=success_message,
                        container=container,
                    ),
                ),
                stdout_type=StdoutType.MACHINE_READABLE,
            )
        except DockerContainerNotFoundError:
            warning_message = (
                f"The Jupyter Notebook service named {container.name} is already stopped."
            )

            self.stdout(
                warning_message,
                severity=StdoutSeverity.WARNING,
            )
            self.stdout(
                dict(
                    JupyterNotebookContainerServiceResponse(
                        action="stop",
                        status="already_stopped",
                        message=warning_message,
                        container=container,
                    ),
                ),
                stdout_type=StdoutType.MACHINE_READABLE,
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

    aliases = ["jnb", "jupyter"]

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
