from time import sleep

from injector import inject

from common import Command, CommandGroup, CommandOption, Settings, StdoutSeverity
from common.container_manager.agents.attention_broker_container_manager import (
    AttentionBrokerManager,
)
from common.container_manager.agents.context_broker_container_manager import (
    ContextBrokerContainerManager,
)
from common.container_manager.agents.evolution_agent_container_manager import (
    EvolutionAgentContainerManager,
)
from common.container_manager.agents.inference_agent_container_manager import (
    InferenceAgentContainerManager,
)
from common.container_manager.agents.link_creation_agent_container_manager import (
    LinkCreationAgentContainerManager,
)
from common.container_manager.agents.query_agent_container_manager import QueryAgentContainerManager
from common.container_manager.atomdb.mongodb_container_manager import MongodbContainerManager
from common.container_manager.atomdb.redis_container_manager import RedisContainerManager
from common.decorators import ensure_container_running
from settings.config import LOG_FILE_NAME

from .logs_docs import (
    HELP_AB,
    HELP_CB,
    HELP_DAS_LOGS,
    HELP_EA,
    HELP_IA,
    HELP_LCA,
    HELP_LOGS,
    HELP_MONGODB,
    HELP_QA,
    HELP_REDIS,
    SHORT_HELP_AB,
    SHORT_HELP_CB,
    SHORT_HELP_DAS_LOGS,
    SHORT_HELP_EA,
    SHORT_HELP_IA,
    SHORT_HELP_LCA,
    SHORT_HELP_LOGS,
    SHORT_HELP_MONGODB,
    SHORT_HELP_QA,
    SHORT_HELP_REDIS,
)


class LogsDas(Command):
    name = "das"

    short_help = SHORT_HELP_DAS_LOGS

    help = HELP_DAS_LOGS

    params = [
        CommandOption(
            ["--follow", "-f"],
            is_flag=True,
            help="Follow log output in real-time.",
            default=False,
            required=False,
        )
    ]

    def __init__(self) -> None:
        super().__init__()

    def _follow_logs(self):
        with open(LOG_FILE_NAME, "r") as file:
            while True:
                line = file.readline()
                if not line:
                    sleep(0.1)
                    continue
                self.stdout(line, new_line=False)

    def _show_logs(self):
        with open(LOG_FILE_NAME, "r") as file:
            for line in file:
                self.stdout(line, new_line=False)

    def run(self, follow: bool = False):
        try:
            if follow:
                self._follow_logs()
            else:
                self._show_logs()
        except KeyboardInterrupt:
            self.stdout("Interrupted. Exiting...", severity=StdoutSeverity.ERROR)
        except FileNotFoundError:
            self.stdout("No logs to show up here", severity=StdoutSeverity.WARNING)


class LogsMongoDb(Command):
    name = "mongodb"

    short_help = SHORT_HELP_MONGODB

    help = HELP_MONGODB

    params = [
        CommandOption(
            ["--follow", "-f"],
            is_flag=True,
            help="Follow log output in real-time.",
            default=False,
            required=False,
        )
    ]

    @inject
    def __init__(
        self,
        settings: Settings,
        mongodb_container_manager: MongodbContainerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._mongodb_container_manager = mongodb_container_manager

    @ensure_container_running(
        ["_mongodb_container_manager"],
        exception_text="MongoDB is not running. Please start it with 'das-cli db start' before viewing logs.",
        verbose=False,
    )
    def run(self, follow: bool = False):
        self._settings.raise_on_missing_file()
        self._settings.raise_on_schema_mismatch()

        self._mongodb_container_manager.logs(follow)


class LogsRedis(Command):
    name = "redis"

    short_help = SHORT_HELP_REDIS

    help = HELP_REDIS

    params = [
        CommandOption(
            ["--follow", "-f"],
            is_flag=True,
            help="Follow log output in real-time.",
            default=False,
            required=False,
        )
    ]

    @inject
    def __init__(
        self,
        settings: Settings,
        redis_container_manager: RedisContainerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._redis_container_manager = redis_container_manager

    @ensure_container_running(
        ["_redis_container_manager"],
        exception_text="Redis is not running. Please start it with 'das-cli db start' before viewing logs.",
        verbose=False,
    )
    def run(self, follow: bool = False):
        self._settings.raise_on_missing_file()
        self._settings.raise_on_schema_mismatch()

        self._redis_container_manager.logs(follow)


class LogsAttentionBroker(Command):
    name = "attention-broker"

    aliases = ["ab"]

    short_help = SHORT_HELP_AB

    help = HELP_AB

    params = [
        CommandOption(
            ["--follow", "-f"],
            is_flag=True,
            help="Follow log output in real-time.",
            default=False,
            required=False,
        )
    ]

    @inject
    def __init__(
        self,
        settings: Settings,
        attention_broker_manager: AttentionBrokerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._attention_broker_manager = attention_broker_manager

    @ensure_container_running(
        ["_attention_broker_manager"],
        exception_text="Attention broker is not running. Please start it with 'das-cli attention-broker start' before viewing logs.",
        verbose=False,
    )
    def run(self, follow: bool = False):
        self._settings.raise_on_missing_file()
        self._settings.raise_on_schema_mismatch()

        self._attention_broker_manager.logs(follow)


class LogsQueryAgent(Command):
    name = "query-agent"

    aliases = ["qa", "query"]

    short_help = SHORT_HELP_QA

    help = HELP_QA

    params = [
        CommandOption(
            ["--follow", "-f"],
            is_flag=True,
            help="Follow log output in real-time.",
            default=False,
            required=False,
        )
    ]

    @inject
    def __init__(
        self,
        settings: Settings,
        query_agent_container_manager: QueryAgentContainerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._query_agent_container_manager = query_agent_container_manager

    @ensure_container_running(
        ["_query_agent_container_manager"],
        exception_text="Query agent is not running. Please start it with 'das-cli query-agent start' before viewing logs.",
        verbose=False,
    )
    def run(self, follow: bool = False):
        self._settings.raise_on_missing_file()
        self._settings.raise_on_schema_mismatch()

        self._query_agent_container_manager.logs(follow)


class LogsLinkCreationAgent(Command):
    name = "link-creation-agent"

    aliases = ["lca"]

    short_help = SHORT_HELP_LCA

    help = HELP_LCA

    params = [
        CommandOption(
            ["--follow", "-f"],
            is_flag=True,
            help="Follow log output in real-time.",
            default=False,
            required=False,
        )
    ]

    @inject
    def __init__(
        self,
        settings: Settings,
        link_creation_container_manager: LinkCreationAgentContainerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._link_creation_container_manager = link_creation_container_manager

    @ensure_container_running(
        ["_link_creation_container_manager"],
        exception_text="Link creation agent is not running. Please start it with 'das-cli link-creation-agent start' before viewing logs.",
        verbose=False,
    )
    def run(self, follow: bool = False):
        self._settings.raise_on_missing_file()
        self._settings.raise_on_schema_mismatch()

        self._link_creation_container_manager.logs(follow)


class LogsInferenceAgent(Command):
    name = "inference-agent"

    aliases = ["inference"]

    short_help = SHORT_HELP_IA

    help = HELP_IA

    params = [
        CommandOption(
            ["--follow", "-f"],
            is_flag=True,
            help="Follow log output in real-time.",
            default=False,
            required=False,
        )
    ]

    @inject
    def __init__(
        self,
        settings: Settings,
        inference_agent_container_manager: InferenceAgentContainerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._inference_agent_container_manager = inference_agent_container_manager

    @ensure_container_running(
        ["_inference_agent_container_manager"],
        exception_text="Inference agent is not running. Please start it with 'das-cli inference-agent start' before viewing logs.",
        verbose=False,
    )
    def run(self, follow: bool = False):
        self._settings.raise_on_missing_file()
        self._settings.raise_on_schema_mismatch()

        self._inference_agent_container_manager.logs(follow)


class LogsEvolutionAgent(Command):
    name = "evolution-agent"

    aliases = ["eb"]

    short_help = SHORT_HELP_EA

    help = HELP_EA

    params = [
        CommandOption(
            ["--follow", "-f"],
            is_flag=True,
            help="Follow log output in real-time.",
            default=False,
            required=False,
        )
    ]

    @inject
    def __init__(
        self,
        settings: Settings,
        evolution_agent_container_manager: EvolutionAgentContainerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._evolution_agent_container_manager = evolution_agent_container_manager

    @ensure_container_running(
        ["_evolution_agent_container_manager"],
        exception_text="Evolution Agent is not running. Please start it with 'das-cli evolution-agent start' before viewing logs.",
        verbose=False,
    )
    def run(self, follow: bool = False):
        self._settings.raise_on_missing_file()
        self._settings.raise_on_schema_mismatch()

        self._evolution_agent_container_manager.logs(follow)


class LogsContextBroker(Command):
    name = "context-broker"

    aliases = ["con", "context"]

    short_help = SHORT_HELP_CB

    help = HELP_CB

    params = [
        CommandOption(
            ["--follow", "-f"],
            is_flag=True,
            help="Follow log output in real-time.",
            default=False,
            required=False,
        )
    ]

    @inject
    def __init__(
        self,
        settings: Settings,
        context_broker_container_manager: ContextBrokerContainerManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._context_broker_container_manager = context_broker_container_manager

    @ensure_container_running(
        ["_context_broker_container_manager"],
        exception_text="Context Broker is not running. Please start it with 'das-cli context-broker start' before viewing logs.",
        verbose=False,
    )
    def run(self, follow: bool = False):
        self._settings.raise_on_missing_file()
        self._settings.raise_on_schema_mismatch()

        self._context_broker_container_manager.logs(follow)


class LogsCli(CommandGroup):
    name = "logs"

    short_help = SHORT_HELP_LOGS

    help = HELP_LOGS

    @inject
    def __init__(
        self,
        logs_das: LogsDas,
        logs_mongodb: LogsMongoDb,
        logs_redis: LogsRedis,
        logs_attention_broker: LogsAttentionBroker,
        logs_query_agent: LogsQueryAgent,
        logs_link_creation_agent: LogsLinkCreationAgent,
        logs_inference_agent: LogsInferenceAgent,
        logs_evolution_agent: LogsEvolutionAgent,
        logs_context_broker: LogsContextBroker,
    ) -> None:
        super().__init__()
        self.add_commands(
            [
                logs_das,
                logs_mongodb,
                logs_redis,
                logs_attention_broker,
                logs_query_agent,
                logs_link_creation_agent,
                logs_inference_agent,
                logs_evolution_agent,
                logs_context_broker,
            ]
        )
