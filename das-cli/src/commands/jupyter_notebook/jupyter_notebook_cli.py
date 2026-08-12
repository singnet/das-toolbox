from injector import inject

import click

from common import Command, CommandGroup, CommandOption, Settings, StdoutSeverity
from common.container_manager.agents.jupyter_notebook_container_manager import (
    JupyterNotebookContainerManager,
)
from common.docker.exceptions import (
    DockerContainerDuplicateError,
    DockerContainerNotFoundError,
    DockerError,
)
from common.exceptions import PortBindingError
from common.prompt_types import AbsolutePath
from common.service_response import ServiceResponse, StdoutStatus, CONTAINER_START_FAILURE_MESSAGE

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

CLI_SERVICE_NAME = "jupyter_notebook"


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
        self._settings.validate_configuration_file()

        container = self._get_container()

        self.log("Starting Jupyter Notebook...", severity=StdoutSeverity.INFO)

        try:
            self._jupyter_notebook_container_manager.start_container(working_dir)
            message = f"Jupyter Notebook started on port {container.port}"

            self.stdout(
                dict(
                    ServiceResponse(
                        service=CLI_SERVICE_NAME,
                        action="start",
                        status=StdoutStatus.SUCCESS,
                        message=message,
                        container=container,
                        working_dir=working_dir,
                    ),
                ),
                severity=StdoutSeverity.SUCCESS,
            )

        except DockerContainerDuplicateError:
            message = (
                f"Jupyter Notebook is already running. It's listening on port {container.port}"
            )

            self.stdout(
                ServiceResponse(
                    service=CLI_SERVICE_NAME,
                    action="start",
                    status=StdoutStatus.INFO,
                    message=message,
                    container=container,
                    working_dir=working_dir,
                ),
                severity=StdoutSeverity.WARNING,
            )

        except (DockerError, PortBindingError) as e:
            self.stdout(
                ServiceResponse(
                    service=CLI_SERVICE_NAME,
                    action="start",
                    status=StdoutStatus.ERROR,
                    message=CONTAINER_START_FAILURE_MESSAGE,
                    error=e,
                    container=container,
                    working_dir=working_dir,
                ),
                severity=StdoutSeverity.ERROR,
            )
            raise click.exceptions.Exit(1)


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
        self._settings.validate_configuration_file()

        container = self._get_container()

        self.log("Stopping jupyter notebook...", severity=StdoutSeverity.INFO)

        try:
            self._jupyter_notebook_container_manager.stop()
            exec_message = "Jupyter Notebook service stopped"

            self.stdout(
                dict(
                    ServiceResponse(
                        service=CLI_SERVICE_NAME,
                        action="stop",
                        status=StdoutStatus.SUCCESS,
                        message=exec_message,
                        container=container,
                    ),
                ),
                severity=StdoutSeverity.SUCCESS,
            )

        except DockerContainerNotFoundError:
            message = f"The Jupyter Notebook service named {container.name} is already stopped."

            self.stdout(
                dict(
                    ServiceResponse(
                        service=CLI_SERVICE_NAME,
                        action="stop",
                        status=StdoutStatus.INFO,
                        message=message,
                        container=container,
                    ),
                ),
                severity=StdoutSeverity.WARNING,
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
