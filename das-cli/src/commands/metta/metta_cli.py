import glob
import os

from injector import inject

from commands.db.mongodb_container_manager import MongodbContainerManager
from commands.db.redis_container_manager import RedisContainerManager
from common import Command, CommandArgument, CommandGroup, Path, Settings, StdoutSeverity
from common.decorators import ensure_container_running
from common.docker.exceptions import DockerError
from common.prompt_types import AbsolutePath

from .metta_loader_container_manager import MettaLoaderContainerManager
from .metta_syntax_container_manager import MettaSyntaxContainerManager


class MettaLoad(Command):
    name = "load"

    short_help = "Load a MeTTa file into the databases."

    help = """
NAME

    das-cli metta load - Load a MeTTa file or directory of files into the database.

SYNOPSIS

    das-cli metta load <path>

DESCRIPTION

    Loads MeTTa files into the configured database using DAS CLI.

    The <path> argument must be an absolute path to a single `.metta` file or a directory
    containing `.metta` files. If a directory is given, all `.metta` files in the directory
    will be loaded. Only files with the `.metta` extension are considered.

    This operation requires that the MongoDB and Redis services are running.
    Use 'das-cli db start' to start the necessary containers before loading.

ARGUMENTS

    <path>

        Absolute path to a .metta file or directory containing .metta files.
        Relative paths are not supported.

EXAMPLES

    Load a single MeTTa file into the database:

        $ das-cli metta load /absolute/path/to/animals.metta

    Load all MeTTa files in a directory:

        $ das-cli metta load /absolute/path/to/mettas-directory
"""

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
        redis_container_manager: RedisContainerManager,
        mongodb_container_manager: MongodbContainerManager,
        metta_loader_container_manager: MettaLoaderContainerManager,
        settings: Settings,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._redis_container_manager = redis_container_manager
        self._mongodb_container_manager = mongodb_container_manager
        self._metta_loader_container_manager = metta_loader_container_manager

    def _load_metta_from_file(self, file_path: str):
        if not file_path.endswith(".metta"):
            self.stdout(
                f"Error: File '{file_path}' is not a .metta file.",
                severity=StdoutSeverity.ERROR,
            )
            return

        self.stdout(f"Loading metta file {file_path}...")

        self._metta_loader_container_manager.start_container(file_path)

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
        [
            "_mongodb_container_manager",
            "_redis_container_manager",
        ],
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

    short_help = "Validate syntax of MeTTa files used with the DAS CLI"

    help = """
NAME

    das-cli metta check - Validate the syntax of MeTTa files without loading them.

SYNOPSIS

    das-cli metta check <path>

DESCRIPTION

    Validates the syntax of a .metta file or all .metta files in a directory.

    This command checks that each MeTTa file is syntactically correct without
    inserting any data into the database. It is useful to catch errors before
    attempting a full load using 'das-cli metta load'.

ARGUMENTS

    <path>

        Absolute path to a .metta file or a directory containing .metta files.
        Relative paths are not supported.

EXAMPLES

    Validate the syntax of a single MeTTa file:

        $ das-cli metta check /absolute/path/to/animals.metta

    Validate the syntax of all files in a directory:

        $ das-cli metta check /absolute/path/to/mettas-directory
"""

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

    short_help = "Manage operations related to the loading of MeTTa files."

    help = """
NAME
    das-cli metta - Manage operations related to MeTTa files.

SYNOPSIS
    das-cli metta <subcommand> [OPTIONS]

DESCRIPTION
    Provides a command group for managing MeTTa knowledge base files. This group
    includes commands for syntax validation and database loading.

    Available subcommands:

        load    Load MeTTa files into the database
        check   Validate syntax of MeTTa files

    Use `das-cli metta check` to quickly check for syntax errors before running
    `das-cli metta load`, which performs the actual data loading.

EXAMPLES
    Check MeTTa syntax before loading:

        $ das-cli metta check /absolute/path/to/mettas-directory

    Load MeTTa files into the database:

        $ das-cli metta load /absolute/path/to/mettas-directory
"""

    @inject
    def __init__(self, metta_load: MettaLoad, metta_check: MettaCheck) -> None:
        super().__init__()
        self.add_commands(
            [
                metta_load,
                metta_check,
            ]
        )
