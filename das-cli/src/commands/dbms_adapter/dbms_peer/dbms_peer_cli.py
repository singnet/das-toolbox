from injector import inject

from commands.dbms_adapter.das_peer.das_peer_container_manager import DasPeerContainerManager
from common import Command, CommandGroup, CommandOption, ImageManager, Settings
from common.docker.exceptions import DockerError
from common.prompt_types import AbsolutePath
from settings.config import DBMS_PEER_IMAGE_NAME, DBMS_PEER_IMAGE_VERSION

from .dbms_peer_container_manager import DbmsPeerContainerManager


class DbmsPeerRun(Command):
    name = "run"

    short_help = "Runs the DBMS peer client to connect with DAS peer server."

    help = """
'das-cli dbms-adapter dbms-peer run' starts the DBMS peer client, enabling it to connect
to the DAS peer server and facilitate data synchronization. This command
establishes a link to the DAS peer using the provided client database credentials
and settings.

To run the command, specify the database connection details including hostname,
port, username, password, and optionally, the database name (defaults to 'postgres').
A context file with necessary configurations is also required.

.SH PARAMETERS

--client-hostname
    Required. Specifies the hostname of the client database to connect to.

--client-port
    Required. Defines the port number on which the client database is running.

--client-username
    Required. The username for authenticating to the client database.

--client-password
    Required. The password for authenticating to the client database.

--client-database
    Optional. Specifies the database name to connect to; defaults to 'postgres' if not provided.

--context
    Required. Path to the context configuration file, which provides additional settings
    necessary for running the DBMS peer client. Must be an absolute path to an existing,
    readable file.

.SH EXAMPLES

To run the DBMS peer client with specified database and context:

$ das-cli dbms-adapter dbms-peer run --client-hostname example.com --client-port 5432 \\
    --client-username user --client-password pass --context /path/to/context.txt
"""

    params = [
        CommandOption(
            ["--client-hostname"],
            help="Specifies the hostname of the client database.",
            type=str,
            required=True,
        ),
        CommandOption(
            ["--client-port"],
            help="Defines the port number of the client database.",
            type=int,
            required=True,
        ),
        CommandOption(
            ["--client-username"],
            help="The username for authenticating to the client database.",
            type=str,
            required=True,
        ),
        CommandOption(
            ["--client-password"],
            help="The password for authenticating to the client database.",
            type=str,
            prompt=True,
            hide_input=True,
            required=True,
        ),
        CommandOption(
            ["--client-database"],
            help="Specifies the database name; defaults to 'postgres'.",
            type=str,
            default="postgres",
            required=False,
        ),
        CommandOption(
            ["--context"],
            help="Path to the configuration file for the DBMS peer client.",
            type=AbsolutePath(
                file_okay=True,
                dir_okay=False,
                exists=True,
                readable=True,
            ),
            required=True,
        ),
    ]

    @inject
    def __init__(
        self,
        settings: Settings,
        image_manager: ImageManager,
        dbms_peer_container_manager: DbmsPeerContainerManager,
        das_peer_container_manager: DasPeerContainerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._image_manager = image_manager
        self._dbms_peer_container_manager = dbms_peer_container_manager
        self._das_peer_container_manager = das_peer_container_manager

    def _start_client(
        self,
        context: str,
        hostname: str,
        port: int,
        username: str,
        password: str,
        database: str,
    ) -> None:
        self.stdout(f"Starting DBMS Peer {hostname}:{port}")

        self._dbms_peer_container_manager.start_container(
            context,
            hostname,
            port,
            username,
            password,
            database,
        )
        self.stdout("Done.")

    def _raise_on_server_not_running(self):
        is_server_running = self._das_peer_container_manager.is_running()

        if not is_server_running:
            raise DockerError(
                "The server is not running. Please start the server by executing `das-peer start` before attempting to run this command."
            )

    def run(
        self,
        context: str,
        client_hostname: str,
        client_port: int,
        client_username: str,
        client_password: str,
        client_database: str,
    ) -> None:
        self._settings.raise_on_missing_file()
        self._settings.raise_on_schema_mismatch()
        self._raise_on_server_not_running()

        self._image_manager.pull(
            DBMS_PEER_IMAGE_NAME,
            DBMS_PEER_IMAGE_VERSION,
        )

        self._start_client(
            context,
            client_hostname,
            client_port,
            client_username,
            client_password,
            client_database,
        )


class DbmsPeerCli(CommandGroup):
    name = "dbms-peer"

    short_help = "Manage DBMS peer client operations."

    help = """
        'das-cli dbms-peer' commands allow management of DBMS peer client operations.
        The DBMS peer acts as a client that connects to the DAS peer server, enabling
        data synchronization and transfer between the DAS peer and the database.

        Using 'das-cli dbms-peer', you can initiate commands to run and configure
        the DBMS peer client with specified connection details.
    """

    @inject
    def __init__(
        self,
        dbms_peer_run: DbmsPeerRun,
    ) -> None:
        super().__init__()
        self.add_commands(
            [
                dbms_peer_run.command,
            ]
        )
