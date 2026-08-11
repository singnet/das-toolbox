from common import Command, StdoutSeverity
from common.container_manager.atomdb.mongodb_container_manager import MongodbContainerManager
from common.container_manager.atomdb.morkdb_container_manager import MorkdbContainerManager
from common.container_manager.atomdb.redis_container_manager import RedisContainerManager
from common.docker.exceptions import DockerContainerDuplicateError, DockerContainerNotFoundError, DockerError
from common.exceptions import PortBindingError
from common.service_response import ServiceResponse, StdoutStatus

CLI_SERVICE_NAME = "database"


class DbOperations:
    def __init__(self, command: Command) -> None:
        self._command = command
        self.errors: list[str] = []

    def reset(self) -> None:
        self.errors = []

    def log(self, message: str, severity: StdoutSeverity = StdoutSeverity.INFO) -> None:
        self._command.log(message, severity=severity)

    def stdout(self, *args, **kwargs) -> None:
        self._command.stdout(*args, **kwargs)

    def get_execution_context(self):
        return self._command.get_execution_context()

    def _resolve_public_ip(self, node_ip: str) -> str:
        return self.get_execution_context().source.get("ip") or node_ip

    def _set_node_context(self, manager, context: str) -> None:
        if context and context != "default":
            manager.set_exec_context(context)
        else:
            manager.unset_exec_context()

    def _record_error(self, message: str) -> None:
        self.errors.append(message)

    def finish(self, action: str, success_message: str, **extra_details) -> None:
        if self.errors:
            error_lines = "\n".join(f"- {error}" for error in self.errors)
            self.stdout(
                dict(
                    ServiceResponse(
                        service=CLI_SERVICE_NAME,
                        action=action,
                        status=StdoutStatus.ERROR,
                        message=f"Database command failed.\n{error_lines}",
                        errors=self.errors,
                        **extra_details,
                    )
                ),
                severity=StdoutSeverity.ERROR,
            )
            return

        self.stdout(
            dict(
                ServiceResponse(
                    service=CLI_SERVICE_NAME,
                    action=action,
                    status=StdoutStatus.SUCCESS,
                    message=success_message,
                    **extra_details,
                )
            ),
            severity=StdoutSeverity.SUCCESS,
        )

    def start_redis(self, manager: RedisContainerManager) -> None:
        self.log("Starting Redis service...", severity=StdoutSeverity.INFO)
        self._start_redis_nodes(manager)

    def _start_redis_nodes(self, manager: RedisContainerManager) -> None:
        options = manager._options
        port = options["redis_port"]
        nodes = options["redis_nodes"]
        cluster = options["redis_cluster"]

        for node in nodes:
            context = node.get("context", "")
            node_username = node.get("username", "")
            node_ip = node.get("ip", "")
            public_ip = self._resolve_public_ip(node_ip)

            try:
                self._set_node_context(manager, context)

                try:
                    manager.start_container(port, node_username, node_ip, cluster)
                    self.log(
                        f"Redis has started successfully on port {port} at {public_ip}, "
                        f"operating under the server user {node_username}.",
                        severity=StdoutSeverity.SUCCESS,
                    )
                except DockerContainerDuplicateError:
                    self.log(
                        f"Redis is already running. It is currently listening on port {port} at "
                        f"{public_ip} under the server user {node_username}.",
                        severity=StdoutSeverity.WARNING,
                    )
                except (DockerError, PortBindingError) as error:
                    self._record_error(
                        f"Failed to start Redis at {public_ip} under {node_username}: {error}"
                    )
            finally:
                manager.unset_exec_context()

        if cluster and not self.errors:
            try:
                manager.start_cluster(nodes, port)
            except Exception as error:
                self._record_error(
                    f"Failed to start Redis cluster. Please check connectivity between nodes: {error}"
                )

    def start_mongodb(self, manager: MongodbContainerManager) -> None:
        self.log("Starting MongoDB service...", severity=StdoutSeverity.INFO)
        self._start_mongo_nodes(manager)

    def _start_mongo_nodes(self, manager: MongodbContainerManager) -> None:
        options = manager._options
        port = options["mongodb_port"]
        nodes = options["mongodb_nodes"]
        cluster = options["mongodb_cluster"]
        username = options["mongodb_username"]
        password = options["mongodb_password"]
        cluster_key = options.get("mongodb_cluster_secret_key")

        for node in nodes:
            context = node.get("context", "")
            node_username = node.get("username", "")
            node_ip = node.get("ip", "")
            public_ip = self._resolve_public_ip(node_ip)
            cluster_node = self._normalize_cluster_node(node) if cluster else None

            try:
                self._set_node_context(manager, context)

                try:
                    manager.start_container(port, username, password, cluster_node, cluster_key)
                    self.log(
                        f"MongoDB has started successfully on port {port} at {public_ip}, "
                        f"operating under the server user {node_username}.",
                        severity=StdoutSeverity.SUCCESS,
                    )
                except DockerContainerDuplicateError:
                    self.log(
                        f"MongoDB is already running. It is currently listening on port {port} at "
                        f"{public_ip} under the server user {node_username}.",
                        severity=StdoutSeverity.WARNING,
                    )
                except (DockerError, PortBindingError) as error:
                    self._record_error(
                        f"Failed to start MongoDB at {public_ip} under {node_username}: {error}"
                    )
            finally:
                manager.unset_exec_context()

        if cluster and not self.errors:
            try:
                manager.start_cluster(nodes, port, username, password)
            except Exception as error:
                self._record_error(
                    f"Failed to start MongoDB cluster. Please check connectivity between nodes: {error}"
                )

    @staticmethod
    def _normalize_cluster_node(node: dict) -> dict:
        return {
            **node,
            "host": node.get("host") or node.get("ip", ""),
        }

    def start_morkdb(self, manager: MorkdbContainerManager) -> None:
        port = manager._options["morkdb_port"]
        self.log("Starting MorkDB service...", severity=StdoutSeverity.INFO)

        try:
            manager.start_container()
            self.log(
                f"MorkDB service has started successfully at port {port}",
                severity=StdoutSeverity.SUCCESS,
            )
        except DockerContainerDuplicateError:
            self.log(f"MorkDB is already running at port {port}", severity=StdoutSeverity.WARNING)
        except (DockerError, PortBindingError) as error:
            self._record_error(f"Failed to start MorkDB at port {port}: {error}")

    def stop_redis(self, manager: RedisContainerManager, *, prune: bool = False) -> None:
        self.log("Stopping Redis service...", severity=StdoutSeverity.INFO)
        self._stop_redis_nodes(manager, prune=prune)

    def _stop_redis_nodes(self, manager: RedisContainerManager, *, prune: bool) -> None:
        nodes = manager._options["redis_nodes"]

        for node in nodes:
            context = node.get("context", "")
            node_ip = node.get("ip", "")
            node_username = node.get("username", "")
            public_ip = self._resolve_public_ip(node_ip)

            try:
                self._set_node_context(manager, context)

                try:
                    manager.stop(remove_volume=prune, force=prune)
                    self.log(
                        f"The Redis service at {public_ip} has been stopped "
                        f"by the server user {node_username}",
                        severity=StdoutSeverity.SUCCESS,
                    )
                except DockerContainerNotFoundError:
                    container_name = manager.get_container().name
                    self.log(
                        f"The Redis service named {container_name} at {public_ip} is already stopped.",
                        severity=StdoutSeverity.WARNING,
                    )
                except (DockerError, PortBindingError) as error:
                    self._record_error(
                        f"Failed to stop Redis at {public_ip} under {node_username}: {error}"
                    )
            finally:
                manager.unset_exec_context()

    def stop_mongodb(self, manager: MongodbContainerManager, *, prune: bool = False) -> None:
        self.log("Stopping MongoDB service...", severity=StdoutSeverity.INFO)
        self._stop_mongo_nodes(manager, prune=prune)

    def _stop_mongo_nodes(self, manager: MongodbContainerManager, *, prune: bool) -> None:
        nodes = manager._options["mongodb_nodes"]

        for node in nodes:
            context = node.get("context", "")
            node_ip = node.get("ip", "")
            node_username = node.get("username", "")
            public_ip = self._resolve_public_ip(node_ip)

            try:
                self._set_node_context(manager, context)

                try:
                    manager.stop(remove_volume=prune, force=prune)
                    self.log(
                        f"The MongoDB service at {public_ip} has been stopped "
                        f"by the server user {node_username}",
                        severity=StdoutSeverity.SUCCESS,
                    )
                except DockerContainerNotFoundError:
                    container_name = manager.get_container().name
                    self.log(
                        f"The MongoDB service named {container_name} at {public_ip} is already stopped.",
                        severity=StdoutSeverity.WARNING,
                    )
                except (DockerError, PortBindingError) as error:
                    self._record_error(
                        f"Failed to stop MongoDB at {public_ip} under {node_username}: {error}"
                    )
            finally:
                manager.unset_exec_context()

    def stop_morkdb(self, manager: MorkdbContainerManager, *, prune: bool = False) -> None:
        self.log("Stopping MorkDB service...", severity=StdoutSeverity.INFO)

        try:
            manager.stop(remove_volume=prune)
            self.log("The service MorkDB has been stopped.", severity=StdoutSeverity.SUCCESS)
        except DockerContainerNotFoundError:
            self.log("The service MorkDB is already stopped.", severity=StdoutSeverity.WARNING)
        except (DockerError, PortBindingError) as error:
            self._record_error(f"Failed to stop MorkDB: {error}")
