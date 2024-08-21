import glob
import os

from injector import inject

from commands.db.mongodb_container_manager import MongodbContainerManager
from commands.db.redis_container_manager import RedisContainerManager
from common import Command, CommandArgument, CommandGroup, Path, Settings, StdoutSeverity
from common.docker.exceptions import DockerContainerNotFoundError, DockerError

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
            type=Path(exists=True),
        )
    ]

    @inject
    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self._settings = settings

    def run(self, path: str):
        self._settings.raise_on_missing_file()

        redis_container_name = self._settings.get("redis.container_name")
        redis_port = self._settings.get("redis.port")

        mongodb_port = self._settings.get("mongodb.port")
        mongodb_container_name = self._settings.get("mongodb.container_name")
        mongodb_username = self._settings.get("mongodb.username")
        mongodb_password = self._settings.get("mongodb.password")

        metta_container_name = self._settings.get("loader.container_name")

        services_not_running = False

        metta_loader_container_manager = MettaLoaderContainerManager(metta_container_name)
        redis_container_manager = RedisContainerManager(redis_container_name)
        mongodb_container_manager = MongodbContainerManager(mongodb_container_name)

        if not redis_container_manager.is_running():
            self.stdout("Redis is not running", severity=StdoutSeverity.ERROR)
            services_not_running = True
        else:

            self.stdout(
                f"Redis is running on port {redis_port}",
                severity=StdoutSeverity.WARNING,
            )

        if not mongodb_container_manager.is_running():
            self.stdout("MongoDB is not running", severity=StdoutSeverity.ERROR)
            services_not_running = True
        else:

            self.stdout(
                f"MongoDB is running on port {mongodb_port}",
                severity=StdoutSeverity.WARNING,
            )

        if services_not_running:
            raise DockerContainerNotFoundError(
                "\nPlease use 'db start' to start required services before running 'metta load'."
            )

        self.stdout("Loading metta file(s)...")

        metta_loader_container_manager.start_container(
            path,
            mongodb_port=mongodb_port,
            mongodb_username=mongodb_username,
            mongodb_password=mongodb_password,
            redis_port=redis_port,
        )
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
