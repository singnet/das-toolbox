import argparse
from cli.commands.list_command import ListCommand
from cli.commands.start_command import StartCommand
from cli.commands.stop_command import StopCommand
from cli.commands.start_agent_command import StartAgentCommand
from cli.commands.restart_agent_command import RestartAgentCommand
from cli.commands.stop_agent_command import StopAgentCommand


class DasRunnerManager:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="DAS Runner Manager CLI")
        self.subparsers = self.parser.add_subparsers()

        self.list_command = ListCommand(self.subparsers)
        self.start_command = StartCommand(self.subparsers)
        self.stop_command = StopCommand(self.subparsers)
        self.start_agent_command = StartAgentCommand(self.subparsers)
        self.restart_agent_command = RestartAgentCommand(self.subparsers)
        self.stop_agent_command = StopAgentCommand(self.subparsers)

    def run(self):
        args = self.parser.parse_args()
        args.func(args)

if __name__ == "__main__":
    manager = DasRunnerManager()
    manager.run()
