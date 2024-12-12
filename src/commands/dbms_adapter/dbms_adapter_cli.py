from injector import inject

from common import CommandGroup

from .das_peer.das_peer_cli import DasPeerCli
from .dbms_peer.dbms_peer_cli import DbmsPeerCli


class DbmsAdapterCli(CommandGroup):
    name = "dbms-adapter"

    short_help = "Groups DBMS and DAS peer server commands for easier management."

    help = """
The 'dbms-adapter' command group provides functionalities for managing both the DAS peer server
and DBMS peer client commands. It allows for organizing and executing operations related to
connecting a DBMS client to the DAS peer server.

This command group includes:
- 'das-peer': Manages DAS peer server operations.
- 'dbms-peer': Manages DBMS peer client operations.

.SH EXAMPLES

To view all commands available in the dbms-adapter group:

$ das-cli dbms-adapter --help

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
