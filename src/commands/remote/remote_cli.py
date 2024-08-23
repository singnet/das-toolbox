from fabric import Connection
from injector import inject

from common import Command, CommandGroup, CommandOption, CommandArgument, StdoutSeverity


class RemoteCommand(Command):
    name = "run"

    short_help = "Run a command on a remote host."

    help = """
    remote host trying to het it done
    """

    params = [
        CommandArgument(["command"], type=str, nargs=-1),
        CommandOption(["--host", "-H"], type=str, help="qwer", required=True),
        CommandOption(["--user", "-U"], type=str, help="qwer", required=False),
        CommandOption(["--port", "-P"], type=str, help="qwer", required=False),
    ]

    def __init__(self) -> None:
        super().__init__()

    def run(self, command, **kwargs):
        breakpoint()
        print("Running remote command...")
        try:
            result = Connection(**kwargs).run(" ".join(command))
        except Exception as e:
            print(e)


class RemoteCli(CommandGroup):
    name = "remote"

    short_help = "Run a command on a remote host."

    help = """
'das-cli remote-command' allows you to run any das-cli command on a remote host.
.SH EXAMPLES:

Update the remote host DAS CLI to the latest version available via APT repository.

$ das-cli remote-command -H <remote_host> -- update-version
"""

    params = []

    @inject
    def __init__(
        self,
        remote: RemoteCommand,
    ) -> None:
        super().__init__()
        self.add_commands(
            [
                remote.command,
            ]
        )
