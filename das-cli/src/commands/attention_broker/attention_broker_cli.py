from typing import AnyStr, Union

from injector import inject

from commands.attention_broker.attention_broker_container_manager import AttentionBrokerManager
from common import Command, CommandGroup, CommandOption, Settings, StdoutSeverity
from common.decorators import ensure_container_running
from common.docker.exceptions import (
    DockerContainerDuplicateError,
    DockerContainerNotFoundError,
    DockerError,
)

class AttentionBrokerStop(Command):
    name = "stop"

    short_help = ""

    help = """
"""

    @inject
    def __init__(
        self,
        settings: Settings,
        attention_broker_manager: AttentionBrokerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._attention_broker_manager = attention_broker_manager


    def _attention_broker(self):
        self.stdout("Stopping Attention Broker service...")


    def run(self):
        self._settings.raise_on_missing_file()

        self._attention_broker()


class AttentionBrokerStart(Command):
    name = "start"

    short_help = ""

    help = """
"""

    @inject
    def __init__(
        self,
        settings: Settings,
        attention_broker_container_manager: AttentionBrokerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._attention_broker_container_manager = attention_broker_container_manager

    def _attention_broker(self) -> None:
        self.stdout("Starting Attention Broker service...")


    def run(self):
        self._settings.raise_on_missing_file()

        self._attention_broker()


class AttentionBrokerRestart(Command):
    name = "restart"

    short_help = ""

    help = """
"""

    @inject
    def __init__(self, attention_broker_start: AttentionBrokerStart, attention_broker_stop: AttentionBrokerStop) -> None:
        super().__init__()
        self._attention_broker_start = attention_broker_start
        self._attention_broker_stop = attention_broker_stop

    def run(self):
        self._attention_broker_stop.run()
        self._attention_broker_start.run()


class AttentionBrokerCli(CommandGroup):
    name = "attention-broker"

    short_help = ""

    help = """
"""

    @inject
    def __init__(
        self,
        attention_broker_start: AttentionBrokerStart,
        attention_broker_stop: AttentionBrokerStop,
        attention_broker_restart: AttentionBrokerRestart,
    ) -> None:
        super().__init__()
        self.add_commands(
            [
                attention_broker_start.command,
                attention_broker_stop.command,
                attention_broker_restart.command,
            ]
        )
