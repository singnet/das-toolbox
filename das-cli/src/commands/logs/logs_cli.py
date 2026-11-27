from time import sleep

from injector import inject

from common import (
    CommandArgument,
    CommandGroup,
    CommandOption,
    IntRange,
    Settings,
    StdoutSeverity,
    StdoutStatus,
)
from common.service_response import ServiceResponse

from common.container_manager.agents.generic_agent_containers import (
    AtomDbBrokerContainerManager,
    AttentionBrokerContainerManager,
    ContextBrokerContainerManager,
    EvolutionAgentContainerManager,
    LCAContainerManager,
    QueryAgentContainerManager,
    MongoDbContainerManager,
    RedisContainerManager,
    MorkDbContainerManager,
)
from common.docker.container_manager import ContainerManager
from settings.config import LOG_FILE_NAME

from .logs_docs import (
    HELP_AB,
    HELP_CB,
    HELP_DAS_LOGS,
    HELP_EA,
    HELP_LCA,
    HELP_LOGS,
    HELP_MONGODB,
    HELP_QA,
    HELP_REDIS,
    SHORT_HELP_AB,
    SHORT_HELP_CB,
    SHORT_HELP_DAS_LOGS,
    SHORT_HELP_EA,
    SHORT_HELP_LCA,
    SHORT_HELP_LOGS,
    SHORT_HELP_MONGODB,
    SHORT_HELP_QA,
    SHORT_HELP_REDIS,
)

CLI_COMMAND_NAME = "logs"

class LogsCli(CommandGroup):

    name = "logs"
    short_help = SHORT_HELP_LOGS
    help = HELP_LOGS

    params = [
        CommandArgument(
            ["service_name"],
            required=True,
            type=str,
        ),
        CommandOption(
            ["--follow", "-f"],
            is_flag=True,
            help="Follow log output in real-time.",
            default=False,
            required=False,
            type=bool,
        ),
        CommandOption(
            ["--tail"],
            type=IntRange(min=1),
            help="Number of lines to show from the end of the logs.",
            default=100,
            show_default=True,
            required=False,
        ),
    ]

    available_containers = {
        "attention-broker" : AttentionBrokerContainerManager,
        "atomdb-broker": AtomDbBrokerContainerManager,
        "context_broker": ContextBrokerContainerManager,
        "evolution-agent": EvolutionAgentContainerManager,
        "link-creation-agent": LCAContainerManager,
        "query-agent": QueryAgentContainerManager,
        "mongodb": MongoDbContainerManager,
        "redis": RedisContainerManager,
        "morkdb": MorkDbContainerManager,
    }
    
    @inject
    def __init__(
        self,
        attention_broker: AttentionBrokerContainerManager,
        atomdb_broker: AtomDbBrokerContainerManager,
        context_broker: ContextBrokerContainerManager,
        evolution_agent: EvolutionAgentContainerManager,
        link_creation_agent: LCAContainerManager,
        query_agent: QueryAgentContainerManager,
        mongodb: MongoDbContainerManager,
        redis: RedisContainerManager,
        morkdb: MorkDbContainerManager,
    ) -> None:
        super().__init__()
        self.override_group_command()
        self.group.allow_interspersed_args = True
        self.group.subcommand_metavar = ""
        self.available_containers = {
            "attention-broker": attention_broker,
            "atomdb-broker": atomdb_broker,
            "context-broker": context_broker,
            "evolution-agent": evolution_agent,
            "link-creation-agent": link_creation_agent,
            "query-agent": query_agent,
            "mongodb": mongodb,
            "redis": redis,
            "morkdb": morkdb,
        }

    def run(self, service_name: str, follow: bool, tail: int):
        container: ContainerManager | None = self.available_containers.get(service_name)

        if container is None:
            self.stdout(
                ServiceResponse(
                    service=CLI_COMMAND_NAME,
                    action="logs",
                    status=StdoutStatus.ERROR,
                    message="The specified service could not be found, cannot fetch container logs.",
                    error="Service not found, cannot fetch the container's logs."
                ),
                StdoutSeverity.ERROR
            )
            return

        container_logs = container.logs(follow=follow, tail=tail)
        try:
            for chunk in container_logs:
                self._emit_log_chunk(service_name, container, chunk)
        except KeyboardInterrupt:
            self.stdout(
                ServiceResponse(
                    service=service_name,
                    action=CLI_COMMAND_NAME,
                    status=StdoutStatus.INFO,
                    message="Interrupted. Exiting...",
                ),
                severity=StdoutSeverity.ERROR,
            )
        finally:
            container_logs.close()

    def _emit_log_chunk(self, service_name: str, container: ContainerManager, chunk: str) -> None:
        self.stdout(
            ServiceResponse(
                service=service_name,
                action=CLI_COMMAND_NAME,
                status=StdoutStatus.INFO,
                message=chunk,
                container=container.get_container(),
            ),
            new_line=False,
        )
