import argparse
from commands.list_command import ListCommand
from commands.start_command import StartCommand
from commands.stop_command import StopCommand

class DasRunnerManager:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="DAS Runner Manager CLI")
        self.subparsers = self.parser.add_subparsers()

        self.list_command = ListCommand(self.subparsers)
        self.start_command = StartCommand(self.subparsers)
        self.stop_command = StopCommand(self.subparsers)

    def run(self):
        args = self.parser.parse_args()
        args.func(args)

if __name__ == "__main__":
    manager = DasRunnerManager()
    manager.run()
