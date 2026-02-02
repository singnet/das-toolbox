import glob
import os

from injector import inject

from common import Command, CommandArgument, CommandGroup, Path, Settings, StdoutSeverity
from common.container_manager.metta.metta_loader_container_manager import (
    MettaLoaderContainerManager,
)
from common.container_manager.metta.metta_mork_loader_container_manager import (
    MettaMorkLoaderContainerManager,
)
from common.container_manager.metta.metta_syntax_container_manager import (
    MettaSyntaxContainerManager,
)
from common.decorators import ensure_container_running
from common.docker.exceptions import DockerError
from common.factory.atomdb.atomdb_backend import AtomdbBackend, AtomdbBackendEnum
from common.prompt_types import AbsolutePath

from .metta_docs import (
    HELP_CHECK,
    HELP_LOAD,
    HELP_METTA,
    SHORT_HELP_CHECK,
    SHORT_HELP_LOAD,
    SHORT_HELP_METTA,
)


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
                exists=True,
                writable=False,
                readable=True,
            ),
        )
    ]

    @inject
    def __init__(
        self,
        atomdb_backend: AtomdbBackend,
        metta_loader_container_manager: MettaLoaderContainerManager,
        metta_mork_loader_container_manager: MettaMorkLoaderContainerManager,
        settings: Settings,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._atomdb_backend = atomdb_backend
        self._metta_loader_container_manager = metta_loader_container_manager
        self._metta_mork_loader_container_manager = metta_mork_loader_container_manager

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
        
        if read and write and execute:
            return
        else:
            raise PermissionError(f"The directory {dir_path} does not have the correct permissions.")

    def _load_metta_from_file(self, file_path: str):
        self.stdout(f"Loading metta file {file_path}...")
        self._check_file_and_permissions(file_path)

        if self._atomdb_backend.name == AtomdbBackendEnum.MORK_MONGODB:
            self._metta_mork_loader_container_manager.start_container(file_path)
        else:
            self._metta_loader_container_manager.start_container(file_path)

    def _load_metta_from_directory(self, directory_path: str):
        self._check_if_directory_has_permissions(dir_path=directory_path)
        files = glob.glob(f"{directory_path}/*")

        for file_path in files:
            try:
                self._load_metta_from_file(file_path)
                self.stdout("Done loading.", severity=StdoutSeverity.SUCCESS)
                
            except Exception as e:
                self.stdout(f"Failed loading file.\nReason: {e}", severity=StdoutSeverity.ERROR)

    def _load_metta(self, path: str):
        isdir = self._check_if_file_or_directory(path)

        if isdir:
            self._load_metta_from_directory(path)
        else:
            self._load_metta_from_file(path)
            self.stdout("Done loading.", severity=StdoutSeverity.SUCCESS)

    @ensure_container_running(
        "_atomdb_backend",
        exception_text="\nPlease use 'db start' to start required services before running 'metta load'.",
        verbose=True,
    )
    def run(self, path: str):
        self._settings.validate_configuration_file()
        self._check_path_exists(path)
        self._load_metta(path)


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

    def check_syntax(self, file_path):
        self._metta_syntax_container_manager.start_container(file_path)

        self.stdout("Checking syntax... OK", severity=StdoutSeverity.SUCCESS)

    def validate_file(self, file_path):
        self.stdout(f"Checking file {file_path}:")
        try:
            self.check_syntax(file_path)
        except IsADirectoryError:
            raise IsADirectoryError(f"The specified path '{file_path}' is a directory.")
        except FileNotFoundError:
            raise FileNotFoundError(f"The specified file path '{file_path}' does not exist.")
        except DockerError:
            self.stdout("Checking syntax... FAILED", severity=StdoutSeverity.ERROR)

    def validate_directory(self, directory_path):
        files = glob.glob(f"{directory_path}/*")
        for file_path in files:
            self.validate_file(file_path)

    def run(self, path: str):
        self._settings.validate_configuration_file()

        if os.path.isdir(path):
            self.validate_directory(
                path,
            )
        else:
            self.validate_file(path)


class MettaCli(CommandGroup):
    name = "metta"

    short_help = SHORT_HELP_METTA

    help = HELP_METTA

    @inject
    def __init__(self, metta_load: MettaLoad, metta_check: MettaCheck) -> None:
        super().__init__()
        self.add_commands(
            [
                metta_load,
                metta_check,
            ]
        )
