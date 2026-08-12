import glob
import os

from injector import inject

from common import Command, CommandArgument, CommandGroup, Path, Settings, StdoutSeverity
from common.container_manager.metta.database_loader_container_manager import (
    DatabaseLoaderContainerManager,
)
from common.container_manager.metta.metta_syntax_container_manager import (
    MettaSyntaxContainerManager,
)
from common.decorators import ensure_container_running
from common.docker.exceptions import DockerError
from common.factory.atomdb.atomdb_backend import AtomdbBackend
from common.prompt_types import AbsolutePath
from common.service_response import ServiceResponse, StdoutStatus

from .metta_docs import (
    HELP_CHECK,
    HELP_LOAD,
    HELP_METTA,
    SHORT_HELP_CHECK,
    SHORT_HELP_LOAD,
    SHORT_HELP_METTA,
)

CLI_SERVICE_NAME = "metta"


class MettaLoad(Command):
    name = "load"

    short_help = SHORT_HELP_LOAD

    help = HELP_LOAD

    params = [
        CommandArgument(
            ["path"],
            type=AbsolutePath(
                dir_okay=True,
                file_okay=True,
                exists=False,
                writable=False,
                readable=False,
            ),
        )
    ]

    @inject
    def __init__(
        self,
        atomdb_backend: AtomdbBackend,
        database_loader_container_manager: DatabaseLoaderContainerManager,
        metta_syntax_container_manager: MettaSyntaxContainerManager,
        settings: Settings,
    ) -> None:
        super().__init__()

        self._settings = settings
        self._atomdb_backend = atomdb_backend
        self._database_loader_container_manager = database_loader_container_manager
        self._metta_syntax_container_manager = metta_syntax_container_manager

    @ensure_container_running(
        "_atomdb_backend",
        exception_text=(
            "\nPlease use 'db start' to start required services " "before running 'metta load'."
        ),
        verbose=True,
    )
    def run(self, path: str):
        self._settings.validate_configuration_file()
        self._check_path_exists(path)

        if self._check_if_file_or_directory(path):
            loaded_files, errors = self._load_metta_from_directory(path)
        else:
            loaded_files, errors = self._load_metta_from_file(path)

        self._finish_load(path, loaded_files, errors)

    def _finish_load(self, path: str, loaded_files: list[str], errors: list[str]) -> None:
        if errors:
            error_lines = "\n".join(f"- {error}" for error in errors)
            self.stdout(
                dict(
                    ServiceResponse(
                        service=CLI_SERVICE_NAME,
                        action="load",
                        status=StdoutStatus.ERROR,
                        message=f"MeTTa load failed for '{path}'.\n{error_lines}",
                        path=path,
                        loaded_files=loaded_files,
                        errors=errors,
                    )
                ),
                severity=StdoutSeverity.ERROR,
            )
            return

        self.stdout(
            dict(
                ServiceResponse(
                    service=CLI_SERVICE_NAME,
                    action="load",
                    status=StdoutStatus.SUCCESS,
                    message=f"MeTTa loaded successfully from '{path}'.",
                    path=path,
                    loaded_files=loaded_files,
                )
            ),
            severity=StdoutSeverity.SUCCESS,
        )

    def _check_path_exists(self, file_path: str):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The specified file path '{file_path}' does not exist.")

    def _check_if_file_or_directory(self, file_path: str):
        return os.path.isdir(file_path)

    def _check_file_and_permissions(self, file_path: str):
        if not file_path.endswith(".metta"):
            raise TypeError(f"Error: File '{file_path}' is not a .metta file.")

        if not os.access(file_path, os.R_OK):
            raise PermissionError(f"The file {file_path} does not have correct permissions.")

    def _check_if_directory_has_permissions(self, dir_path: str):
        read = os.access(dir_path, os.R_OK)
        write = os.access(dir_path, os.W_OK)
        execute = os.access(dir_path, os.X_OK)

        if not (read and write and execute):
            raise PermissionError(
                f"The directory {dir_path} does not have the correct permissions."
            )

    def _validate_metta_syntax(self, file_path: str):
        try:
            self._metta_syntax_container_manager.start_container(file_path)
        except DockerError as error:
            raise DockerError(
                f"Syntax validation failed for '{file_path}'. "
                "The file contains invalid MeTTa syntax."
            ) from error

    def _load_metta_from_file(self, file_path: str) -> tuple[list[str], list[str]]:
        self.log(f"Loading metta file {file_path}...", severity=StdoutSeverity.INFO)

        self._check_file_and_permissions(file_path)

        self.log("Validating syntax...", severity=StdoutSeverity.INFO)
        self._validate_metta_syntax(file_path)
        self.log("Syntax validation passed.", severity=StdoutSeverity.SUCCESS)

        self._database_loader_container_manager.start_container(file_path)
        self.log(f"Done loading {file_path}.", severity=StdoutSeverity.SUCCESS)

        return [file_path], []

    def _load_metta_from_directory(self, directory_path: str) -> tuple[list[str], list[str]]:
        self._check_if_directory_has_permissions(directory_path)

        loaded_files: list[str] = []
        errors: list[str] = []

        for file_path in glob.glob(f"{directory_path}/*"):
            try:
                file_loaded, _ = self._load_metta_from_file(file_path)
                loaded_files.extend(file_loaded)
            except Exception as error:
                message = f"Failed loading '{file_path}': {error}"
                errors.append(message)
                self.log(message, severity=StdoutSeverity.ERROR)

        return loaded_files, errors


class MettaCheck(Command):
    name = "check"

    short_help = SHORT_HELP_CHECK

    help = HELP_CHECK

    params = [
        CommandArgument(
            ["path"],
            type=Path(exists=True),
        )
    ]

    @inject
    def __init__(
        self,
        metta_syntax_container_manager: MettaSyntaxContainerManager,
        settings: Settings,
    ) -> None:
        super().__init__()
        self._metta_syntax_container_manager = metta_syntax_container_manager
        self._settings = settings

    def run(self, path: str):
        self._settings.validate_configuration_file()

        if os.path.isdir(path):
            checked_files, errors = self._validate_directory(path)
        else:
            checked_files, errors = self._validate_file(path)

        self._finish_check(path, checked_files, errors)

    def _finish_check(self, path: str, checked_files: list[str], errors: list[str]) -> None:
        if errors:
            error_lines = "\n".join(f"- {error}" for error in errors)
            self.stdout(
                dict(
                    ServiceResponse(
                        service=CLI_SERVICE_NAME,
                        action="check",
                        status=StdoutStatus.ERROR,
                        message=f"MeTTa syntax check failed for '{path}'.\n{error_lines}",
                        path=path,
                        checked_files=checked_files,
                        errors=errors,
                    )
                ),
                severity=StdoutSeverity.ERROR,
            )
            return

        self.stdout(
            dict(
                ServiceResponse(
                    service=CLI_SERVICE_NAME,
                    action="check",
                    status=StdoutStatus.SUCCESS,
                    message=f"MeTTa syntax check passed for '{path}'.",
                    path=path,
                    checked_files=checked_files,
                )
            ),
            severity=StdoutSeverity.SUCCESS,
        )

    def _check_syntax(self, file_path: str) -> None:
        self._metta_syntax_container_manager.start_container(file_path)
        self.log(f"Checking syntax for {file_path}... OK", severity=StdoutSeverity.SUCCESS)

    def _validate_file(self, file_path: str) -> tuple[list[str], list[str]]:
        self.log(f"Checking file {file_path}:", severity=StdoutSeverity.INFO)

        try:
            self._check_syntax(file_path)
            return [file_path], []
        except IsADirectoryError as error:
            raise IsADirectoryError(f"The specified path '{file_path}' is a directory.") from error
        except FileNotFoundError as error:
            raise FileNotFoundError(
                f"The specified file path '{file_path}' does not exist."
            ) from error
        except DockerError as error:
            message = f"Checking syntax for {file_path}... FAILED: {error}"
            self.log(message, severity=StdoutSeverity.ERROR)
            return [], [message]

    def _validate_directory(self, directory_path: str) -> tuple[list[str], list[str]]:
        checked_files: list[str] = []
        errors: list[str] = []

        for file_path in glob.glob(f"{directory_path}/*"):
            file_checked, file_errors = self._validate_file(file_path)
            checked_files.extend(file_checked)
            errors.extend(file_errors)

        return checked_files, errors


class MettaCli(CommandGroup):
    name = "metta"

    short_help = SHORT_HELP_METTA

    help = HELP_METTA

    @inject
    def __init__(
        self,
        metta_load: MettaLoad,
        metta_check: MettaCheck,
    ) -> None:
        super().__init__()

        self.add_commands(
            [
                metta_load,
                metta_check,
            ]
        )
