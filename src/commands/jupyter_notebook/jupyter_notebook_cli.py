from injector import inject

from common import Command, CommandGroup, Settings, StdoutSeverity
from common.docker.exceptions import (
    DockerContainerDuplicateError,
    DockerContainerNotFoundError,
    DockerError,
)

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
"""

    @inject
    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self._settings = settings

    def run(self):
        self._settings.raise_on_missing_file()

        self.stdout("Starting Jupyter Notebook...")

        jupyter_notebook_container_name = self._settings.get("jupyter_notebook.container_name")
        jupyter_notebook_port = self._settings.get("jupyter_notebook.port")

        try:
            jupyter_notebook_service = JupyterNotebookContainerManager(
                jupyter_notebook_container_name
            )

            jupyter_notebook_service.start_container(
                jupyter_notebook_port,
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
    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self._settings = settings

    def run(self):
        self._settings.raise_on_missing_file()

        self.stdout("Stopping jupyter notebook...")

        jupyter_notebook_container_name = self._settings.get("jupyter_notebook.container_name")

        try:
            JupyterNotebookContainerManager(jupyter_notebook_container_name).stop()
            self.stdout(
                "Jupyter Notebook service stopped",
                severity=StdoutSeverity.SUCCESS,
            )
        except DockerContainerNotFoundError:
            self.stdout(
                f"The Jupyter Notebook service named {jupyter_notebook_container_name} is already stopped.",
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
"""

    @inject
    def __init__(
        self,
        jupyter_notebook_start: JupyterNotebookStart,
        jupyter_notebook_stop: JupyterNotebookStop,
    ) -> None:
        super().__init__()
        self._jupyter_notebook_start = jupyter_notebook_start
        self._jupyter_notebook_stop = jupyter_notebook_stop

    def run(self):
        self._jupyter_notebook_stop.run()
        self._jupyter_notebook_start.run()


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
