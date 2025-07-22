from injector import inject

from commands.dbms_adapter.das_peer.das_peer_container_manager import (
    DasPeerContainerManager,
)
from common import (
    Command,
    CommandGroup,
    CommandOption,
    ImageManager,
    Settings,
    StdoutSeverity,
    StdoutType,
    Container,
)
from common.decorators import ensure_container_running
from common.prompt_types import AbsolutePath
from settings.config import DBMS_PEER_IMAGE_NAME, DBMS_PEER_IMAGE_VERSION

from .dbms_peer_container_manager import DbmsPeerContainerManager
from .dbms_peer_container_service_response import DbmsPeerContainerServiceResponse


class DbmsPeerRun(Command):
    name = "run"

    short_help = "Runs the DBMS peer client to connect with DAS peer server."

    help = """
NAME

    das-cli dbms-adapter dbms-peer run - Run the DBMS peer client to connect with DAS peer server.

SYNOPSIS

    das-cli dbms-adapter dbms-peer run [OPTIONS]

DESCRIPTION

    Start the DBMS peer client, which connects to the DAS peer server to facilitate
    data synchronization between a client-side PostgreSQL database and the DAS Atomspace.

    This command initializes a containerized DBMS peer using the given database
    credentials and a context configuration file. The context file must be an existing,
    readable file that contains all necessary runtime parameters.

OPTIONS

    --client-hostname TEXT     Required. Hostname of the client PostgreSQL database.
    --client-port INTEGER      Required. Port of the client PostgreSQL database.
    --client-username TEXT     Required. Username to authenticate with the database.
    --client-password TEXT     Required. Password to authenticate with the database (prompted securely).
    --client-database TEXT     Optional. Defaults to 'postgres' if not specified.
    --context PATH             Required. Absolute path to the context configuration file.

NOTES

    - The DAS peer server must be running before this command can be executed.
      If it is not running, an error will be raised.

    - The Docker image for the DBMS peer will be pulled if not already available.

EXAMPLES

    Run the DBMS peer to sync data from a PostgreSQL database:

        das-cli dbms-adapter dbms-peer run \\
            --client-hostname db.internal \\
            --client-port 5432 \\
            --client-username admin \\
            --client-password secret \\
            --client-database das_data \\
            --context /etc/das/context.txt
"""

    params = [
        CommandOption(
            ["--client-hostname"],
            help="Specifies the hostname of the client database.",
            type=str,
            prompt="Enter client database hostname (e.g., localhost)",
        ),
        CommandOption(
            ["--client-port"],
            help="Defines the port number of the client database.",
            type=int,
            prompt="Enter client database port (e.g., 5432)",
        ),
        CommandOption(
            ["--client-username"],
            help="The username for authenticating to the client database.",
            type=str,
            prompt="Enter client database username",
        ),
        CommandOption(
            ["--client-password"],
            help="The password for authenticating to the client database.",
            type=str,
            hide_input=True,
            prompt="Enter client database password",
        ),
        CommandOption(
            ["--client-database"],
            help="Specifies the database name; defaults to 'postgres'.",
            type=str,
            default="postgres",
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
            prompt="Enter path to DBMS peer client config file",
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

    def _get_container(self) -> Container:
        return self._dbms_peer_container_manager.get_container()

    def _start_client(
        self,
        context: str,
        hostname: str,
        port: int,
        username: str,
        password: str,
        database: str,
    ) -> None:
        self.stdout(
            f"Starting DBMS Peer {hostname}:{port}",
            severity=StdoutSeverity.INFO,
        )

        show_logs = self.output_format == "plain"

        self._dbms_peer_container_manager.start_container(
            context,
            hostname,
            port,
            username,
            password,
            database,
            show_logs,
        )

        success_message = (
            f"DBMS Peer client started successfully on {hostname}:{port}. "
            "It will now connect to the DAS peer server and synchronize data."
        )

        self.stdout(
            success_message,
            severity=StdoutSeverity.SUCCESS,
        )
        self.stdout(
            dict(
                DbmsPeerContainerServiceResponse(
                    action="run",
                    status="success",
                    message=success_message,
                    container=self._get_container(),
                    extra_details={
                        "client": {
                            "context": context,
                            "hostname": hostname,
                            "port": port,
                            "username": username,
                            "database": database,
                        },
                    },
                ),
            ),
            stdout_type=StdoutType.MACHINE_READABLE,
        )

    @ensure_container_running(
        [
            "_das_peer_container_manager",
        ],
        exception_text="\nThe server is not running. Please start the server by executing `das-peer start` before attempting to run this command.",
        verbose=False,
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

    aliases = ["dbp", "dbpeer", "dbmspeer"]

    short_help = "Manage DBMS peer client operations."

    help = """
NAME

    das-cli dbms-adapter dbms-peer - Manage DBMS peer client operations.

SYNOPSIS

    das-cli dbms-adapter dbms-peer <command> [OPTIONS]

DESCRIPTION

    Commands under 'das-cli dbms-adapter dbms-peer' allow you to manage and
    execute DBMS peer client operations.

    The DBMS peer acts as a client component that connects to the DAS peer server,
    enabling data synchronization and communication between an external PostgreSQL
    database and the Distributed Atomspace (DAS).

    Use this command group to run and configure the DBMS peer client with the
    appropriate connection parameters and context file.

SUBCOMMANDS

    run     Start the DBMS peer client using specified database and context options.

EXAMPLES

    Run the DBMS peer client:

        das-cli dbms-adapter dbms-peer run \\
            --client-hostname localhost \\
            --client-port 5432 \\
            --client-username das \\
            --client-password secret \\
            --context /etc/das/context.txt
"""

    @inject
    def __init__(
        self,
        dbms_peer_run: DbmsPeerRun,
    ) -> None:
        super().__init__()
        self.add_commands(
            [
                dbms_peer_run,
            ]
        )
