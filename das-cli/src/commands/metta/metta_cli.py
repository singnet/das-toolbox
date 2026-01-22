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

from .metta_docs import *

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

    def _load_metta_from_file(self, file_path: str):
        if not file_path.endswith(".metta"):
            self.stdout(
                f"Error: File '{file_path}' is not a .metta file.",
                severity=StdoutSeverity.ERROR,
            )
            return

        self.stdout(f"Loading metta file {file_path}...")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The specified file path '{file_path}' does not exist.")

        if not os.path.isfile(file_path):
            raise IsADirectoryError(f"The specified path '{file_path}' is a directory.")

        self._metta_loader_container_manager.start_container(file_path)

        if self._atomdb_backend.name == AtomdbBackendEnum.MORK_MONGODB:
            self._metta_mork_loader_container_manager.start_container(file_path)

    def _load_metta_from_directory(self, directory_path: str):
        files = glob.glob(f"{directory_path}/*")
        for file_path in files:
            try:
                self._load_metta_from_file(file_path)
            except Exception:
                pass

    def _load_metta(self, path: str):
        if os.path.isdir(path):
            self._load_metta_from_directory(path)
        else:
            self._load_metta_from_file(path)

    @ensure_container_running(
        "_atomdb_backend",
        exception_text="\nPlease use 'db start' to start required services before running 'metta load'.",
        verbose=True,
    )
    def run(self, path: str):
        self._settings.raise_on_missing_file()
        self._settings.raise_on_schema_mismatch()

        self._load_metta(path)

        self.stdout("Done.")


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
        self._settings.raise_on_missing_file()
        self._settings.raise_on_schema_mismatch()

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
