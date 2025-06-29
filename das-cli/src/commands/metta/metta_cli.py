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
'das-cli meta load' loads meta files into the database using the DAS CLI.
The <path> argument specifies the absolute path (relative paths are not supported) to a MeTTa file to be loaded into the database.
Depending on the size of the file and the configuration of your server, loading may take a considerable amount of time.
Before using this command, make sure that the database is running using the 'das-cli db start' command.

.SH EXAMPLES

Load a meta file into the database.

$ das-cli meta load /path/to/mettas-directory/animals.metta
"""

    params = [
        CommandArgument(
            ["path"],
            type=AbsolutePath(
                dir_okay=True,
                file_okay=True,
                exists=True,
                writable=True,
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
                f"Error: File '{file_path}' is not a .metta file.", severity=StdoutSeverity.ERROR
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
'das-cli metta check' just validates the syntax of a MeTTa file without actually loading it.
The <path> argument specifies the absolute path (relative paths are not supported) to a MeTTa file.

.SH EXAMPLES

Validate the syntax of a MeTTa files.

$ das-cli metta check /path/to/mettas-directory

Validate the syntax of a specific metta file.

$ das-cli metta check /path/to/mettas-directory/animals.metta
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

    help = "'das-cli metta' allows you to load or just validate the syntax of MeTTa files. Syntax check is a lot faster than actually loading the file so it may be useful to do it before loading very large files."

    @inject
    def __init__(self, metta_load: MettaLoad, metta_check: MettaCheck) -> None:
        super().__init__()
        self.add_commands(
            [
                metta_load.command,
                metta_check.command,
            ]
        )
