from injector import inject

from common import CommandGroup

from .das_peer.das_peer_cli import DasPeerCli
from .dbms_peer.dbms_peer_cli import DbmsPeerCli


class DbmsAdapterCli(CommandGroup):
    name = "dbms-adapter"

    short_help = "Groups DBMS and DAS peer server commands for easier management."

    help = """
NAME

    das-cli dbms-adapter - Group commands for managing the DAS peer server and DBMS peer client.

SYNOPSIS

    das-cli dbms-adapter <command> [OPTIONS]

DESCRIPTION

    The 'dbms-adapter' command group provides an organized interface for managing both the
    DAS peer server and the DBMS peer client components. These commands facilitate the
    setup and operation of the DAS peer-to-peer communication and database synchronization layer.

    The group contains the following subcommands:

COMMANDS

    das-peer      Manage the DAS peer server operations, such as starting or stopping the container.
    dbms-peer     Manage the DBMS peer client operations, such as connecting to the DAS peer.

EXAMPLES

    View available commands in the dbms-adapter group:

        das-cli dbms-adapter --help

    Run the DAS peer server:

        das-cli dbms-adapter das-peer start --context /etc/das/context.txt

    Run the DBMS peer client:

        das-cli dbms-adapter dbms-peer run \\
            --client-hostname db.example.org \\
            --client-port 5432 \\
            --client-username user \\
            --client-password pass \\
            --context /etc/das/context.txt
"""

    @inject
    def __init__(
        self,
        das_peer_cli: DasPeerCli,
        dbms_peer: DbmsPeerCli,
    ) -> None:
        super().__init__()
        self.add_commands(
            [
                das_peer_cli.group,
                dbms_peer.group,
            ]
        )
