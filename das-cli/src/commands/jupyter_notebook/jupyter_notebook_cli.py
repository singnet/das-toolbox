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
'das-cli jupyter-notebook start' starts a Jupyter Notebook environment.
This command launches a Jupyter server on your local machine, allowing you to create, edit, and run Python notebooks interactively in your web browser.
After starting the Jupyter Notebook environment, the command will display the port in your terminal.
You can access the Jupyter Notebook by navigating to localhost using the displayed port number in your web browser.
There is no token or password required for access.

.SH EXAMPLES

Start a Jupyter Notebook environment.

$ das-cli jupyter-notebook start

Start a Jupyter Notebook environment with a custom working directory.

$ das-cli jupyter-notebook start --working-dir /path/to/working/directory
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
'das-cli jupyter-notebook stop' stops a running Jupyter Notebook environment.

.SH EXAMPLES

Stop a running Jupyter Notebook environment.

$ das-cli jupyter-notebook stop
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
'das-cli jupyter-notebook restart' restarts a Jupyter Notebook environment.
This command stops the currently running Jupyter server, then starts a new instance of the server, effectively restarting the environment.

.SH EXAMPLES

Restart a Jupyter Notebook environment.

$ das-cli jupyter-notebook restart

Restart a Jupyter Notebook environment with a custom working directory.

$ das-cli jupyter-notebook restart --working-dir /path/to/working/directory
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

    help = "'das-cli jupyter-notebook' allows you to manage Jupyter Notebook environments providing commands to start, stop, and restart Jupyter Notebook servers, enabling you to interactively create, edit, and run Python notebooks."

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
                jupyter_notebook_start.command,
                jupyter_notebook_stop.command,
                jupyter_notebook_restart.command,
            ]
        )
