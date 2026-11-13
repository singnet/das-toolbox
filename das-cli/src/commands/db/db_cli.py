from injector import inject

from common import Command, CommandGroup, CommandOption, Settings, StdoutSeverity
from common.container_manager.atomdb.mongodb_container_manager import MongodbContainerManager
from common.decorators import ensure_container_running
from common.factory.atomdb.atomdb_backend import AtomdbBackend
from common.service_response import ServiceResponse, StdoutStatus

from .db_docs import (
    HELP_DB_CLI,
    HELP_DB_COUNT_ATOMS,
    HELP_DB_RESTART,
    HELP_DB_START,
    HELP_DB_STOP,
    SHORT_HELP_DB_CLI,
    SHORT_HELP_DB_COUNT_ATOMS,
    SHORT_HELP_DB_RESTART,
    SHORT_HELP_DB_START,
    SHORT_HELP_DB_STOP,
)
from .db_services import CLI_SERVICE_NAME, DbOperations, run_configured_backends


class DbCountAtoms(Command):
    name = "count-atoms"

    short_help = SHORT_HELP_DB_COUNT_ATOMS

    help = HELP_DB_COUNT_ATOMS

    @inject
    def __init__(
        self,
        atomdb_backend: AtomdbBackend,
    ) -> None:
        self._atomdb_backend = atomdb_backend

        super().__init__()

    def _show_mongodb_stats(self, manager: MongodbContainerManager):
        nodes = manager._options.get("mongodb_nodes") or []
        context = nodes[0].get("context", "") if nodes else ""

        try:
            if context and context != "default":
                manager.set_exec_context(context)
            else:
                manager.unset_exec_context()
            collection_stats = manager.get_collection_stats()
        finally:
            manager.unset_exec_context()

        container = manager.get_container()

        if len(collection_stats) < 1:
            self.log("MongoDB: No collections found (0)", severity=StdoutSeverity.WARNING)
            return self.stdout(
                dict(
                    ServiceResponse(
                        service=CLI_SERVICE_NAME,
                        action="count-atoms",
                        status=StdoutStatus.INFO,
                        message="No MongoDB collections found.",
                        container=container,
                        stats=collection_stats,
                    )
                ),
                severity=StdoutSeverity.WARNING,
            )

        for key, count in collection_stats.items():
            self.log(f"MongoDB {key}: {count}", severity=StdoutSeverity.INFO)

        self.stdout(
            dict(
                ServiceResponse(
                    service=CLI_SERVICE_NAME,
                    action="count-atoms",
                    status=StdoutStatus.SUCCESS,
                    message="Count of MongoDB atoms displayed successfully.",
                    container=container,
                    stats=collection_stats,
                )
            ),
            severity=StdoutSeverity.SUCCESS,
        )

    @ensure_container_running(
        "_atomdb_backend",
        exception_text="\nPlease use 'db start' to start required services before running 'db count-atoms'.",
        verbose=False,
    )
    def run(self) -> None:
        for provider in self._atomdb_backend.get_active_providers():
            manager = getattr(provider, "mongodb_container_manager", None)
            if manager is None:
                continue
            peer_uid = getattr(provider, "peer_uid", None)
            if peer_uid:
                self.log(f"Counting atoms on RemoteDB local persistence {peer_uid}...")
            self._show_mongodb_stats(manager)


class DbStop(Command):
    name = "stop"

    params = [
        CommandOption(
            ["--prune", "-p"],
            is_flag=True,
            help="Remove volumes and force stop the containers.",
            default=False,
            required=False,
        ),
    ]

    short_help = SHORT_HELP_DB_STOP
    help = HELP_DB_STOP

    @inject
    def __init__(
        self,
        settings: Settings,
        atomdb_backend: AtomdbBackend,
    ) -> None:
        self._settings = settings
        self._atomdb_backend = atomdb_backend
        self._db = DbOperations(self)
        super().__init__()

    def run(self, prune: bool = False) -> None:
        self._settings.validate_configuration_file()
        self._db.reset()
        run_configured_backends(self, "stop", prune=prune)
        self._db.finish("stop", "Database services stopped successfully.", prune=prune)


class DbStart(Command):
    name = "start"
    short_help = SHORT_HELP_DB_START
    help = HELP_DB_START

    @inject
    def __init__(
        self,
        settings: Settings,
        atomdb_backend: AtomdbBackend,
    ) -> None:
        self._settings = settings
        self._atomdb_backend = atomdb_backend
        self._db = DbOperations(self)
        super().__init__()

    def run(self):
        self._settings.validate_configuration_file()
        self._db.reset()
        run_configured_backends(self, "start")
        self._db.finish("start", "Database services started successfully.")


class DbRestart(Command):
    name = "restart"

    params = [
        CommandOption(
            ["--prune", "-p"],
            is_flag=True,
            help="Remove volumes and force stop the containers.",
            default=False,
            required=False,
        ),
    ]

    short_help = SHORT_HELP_DB_RESTART

    help = HELP_DB_RESTART

    @inject
    def __init__(self, db_start: DbStart, db_stop: DbStop) -> None:
        super().__init__()
        self._db_start = db_start
        self._db_stop = db_stop

    def run(self, prune: bool = False):
        self.run_subcommand(self._db_stop, prune)
        self.run_subcommand(self._db_start)


class DbCli(CommandGroup):
    name = "database"

    aliases = ["db"]

    short_help = SHORT_HELP_DB_CLI

    help = HELP_DB_CLI

    @inject
    def __init__(
        self,
        db_start: DbStart,
        db_stop: DbStop,
        db_restart: DbRestart,
        db_count_atoms: DbCountAtoms,
    ) -> None:
        super().__init__()
        self.add_commands(
            [
                db_start,
                db_stop,
                db_restart,
                db_count_atoms,
            ]
        )
