from .start_agent_command import StartAgentCommand
from .stop_agent_command import StopAgentCommand

class RestartAgentCommand:
    def __init__(self, subparsers):
        self.parser = subparsers.add_parser("restart-agent", help="Restarts the agent container")
        self.parser.set_defaults(func=self.run)

        self.stop_agent_cmd = StopAgentCommand(subparsers)
        self.start_agent_cmd = StartAgentCommand(subparsers)

    def run(self, args):
        self.stop_agent_cmd.run(args)
        self.start_agent_cmd.run(args)