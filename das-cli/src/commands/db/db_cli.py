from injector import inject

from common import Command, CommandGroup, CommandOption, Settings, StdoutSeverity
from common.container_manager.atomdb.mongodb_container_manager import MongodbContainerManager
from common.container_manager.atomdb.morkdb_container_manager import MorkdbContainerManager
from common.container_manager.atomdb.redis_container_manager import RedisContainerManager
from common.decorators import ensure_container_running
from common.factory.atomdb.atomdb_backend import (
    AtomdbBackend,
    MongoDBRedisBackend,
    MorkMongoDBBackend,
)
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
from .db_services import CLI_SERVICE_NAME, DbOperations


class DbCountAtoms(Command):
    name = "count-atoms"

    short_help = SHORT_HELP_DB_COUNT_ATOMS

    help = HELP_DB_COUNT_ATOMS

    @inject
    def __init__(
        self,
        atomdb_backend: AtomdbBackend,
        mongodb_container_manager: MongodbContainerManager,
        redis_container_manager: RedisContainerManager,
    ) -> None:
        self._atomdb_backend = atomdb_backend
        self._mongodb_container_manager = mongodb_container_manager
        self._redis_container_manager = redis_container_manager

        super().__init__()

    def _get_mongodb_container(self):
        return self._mongodb_container_manager.get_container()

    def _show_mongodb_stats(self):
        collection_stats = self._mongodb_container_manager.get_collection_stats()

        if len(collection_stats) < 1:
            self.log("MongoDB: No collections found (0)", severity=StdoutSeverity.WARNING)
            return self.stdout(
                dict(
                    ServiceResponse(
                        service=CLI_SERVICE_NAME,
                        action="count-atoms",
                        status=StdoutStatus.INFO,
                        message="No MongoDB collections found.",
                        container=self._get_mongodb_container(),
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
                    container=self._get_mongodb_container(),
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
            if isinstance(provider, (MongoDBRedisBackend, MorkMongoDBBackend)):
                self._show_mongodb_stats()


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
        redis_container_manager: RedisContainerManager,
        mongodb_container_manager: MongodbContainerManager,
        morkdb_container_manager: MorkdbContainerManager,
    ) -> None:
        self._settings = settings
        self._atomdb_backend = atomdb_backend
        self._redis_container_manager = redis_container_manager
        self._mongodb_container_manager = mongodb_container_manager
        self._morkdb_container_manager = morkdb_container_manager
        self._db = DbOperations(self)
        super().__init__()

    def run(self, prune: bool = False) -> None:
        self._settings.validate_configuration_file()
        self._db.reset()

        for provider in self._atomdb_backend.get_active_providers():
            if isinstance(provider, MongoDBRedisBackend):
                self._db.stop_redis(self._redis_container_manager, prune=prune)
                self._db.stop_mongodb(self._mongodb_container_manager, prune=prune)

            elif isinstance(provider, MorkMongoDBBackend):
                self._db.stop_mongodb(self._mongodb_container_manager, prune=prune)
                self._db.stop_morkdb(self._morkdb_container_manager, prune=prune)

            else:
                self.log(
                    "InMemoryDB and RemoteDB are not supported on the 'db stop' command",
                    severity=StdoutSeverity.WARNING,
                )

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
        redis_container_manager: RedisContainerManager,
        mongodb_container_manager: MongodbContainerManager,
        morkdb_container_manager: MorkdbContainerManager,
    ) -> None:
        self._settings = settings
        self._atomdb_backend = atomdb_backend
        self._redis_container_manager = redis_container_manager
        self._mongodb_container_manager = mongodb_container_manager
        self._morkdb_container_manager = morkdb_container_manager
        self._db = DbOperations(self)
        super().__init__()

    def run(self):
        self._settings.validate_configuration_file()
        self._db.reset()

        for provider in self._atomdb_backend.get_active_providers():
            if isinstance(provider, MongoDBRedisBackend):
                self._db.start_redis(self._redis_container_manager)
                self._db.start_mongodb(self._mongodb_container_manager)

            elif isinstance(provider, MorkMongoDBBackend):
                self._db.start_mongodb(self._mongodb_container_manager)
                self._db.start_morkdb(self._morkdb_container_manager)

            else:
                self.log(
                    "InMemoryDB and RemoteDB are not supported on the 'db start' command",
                    severity=StdoutSeverity.WARNING,
                )

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
        self._db_stop.run(prune)
        self._db_start.run()


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
