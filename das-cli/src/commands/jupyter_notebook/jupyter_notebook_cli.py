from injector import inject

from common import Command, CommandGroup, CommandOption, Settings, StdoutSeverity, StdoutType
from common.container_manager.agents.jupyter_notebook_container_manager import (
    JupyterNotebookContainerManager,
)
from common.docker.exceptions import (
    DockerContainerDuplicateError,
    DockerContainerNotFoundError,
    DockerError,
)
from common.prompt_types import AbsolutePath

from .jupyter_docs import (
    HELP_JUPYTER,
    HELP_RESTART,
    HELP_START,
    HELP_STOP,
    SHORT_HELP_JUPYTER,
    SHORT_HELP_RESTART,
    SHORT_HELP_START,
    SHORT_HELP_STOP,
)
from .jupyter_notebook_agent_container_service_response import (
    JupyterNotebookContainerServiceResponse,
)


class JupyterNotebookStart(Command):
    name = "start"

    short_help = SHORT_HELP_START

    help = HELP_START

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

    short_help = SHORT_HELP_STOP

    help = HELP_STOP

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

    short_help = SHORT_HELP_RESTART

    help = HELP_RESTART

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

    short_help = SHORT_HELP_JUPYTER

    help = HELP_JUPYTER

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
