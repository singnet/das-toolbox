from injector import inject

from commands.db.mongodb_container_manager import MongodbContainerManager
from commands.db.redis_container_manager import RedisContainerManager
from common import (
    Choice,
    Command,
    CommandGroup,
    CommandOption,
    FunctionVersion,
    ImageManager,
    Settings,
    StdoutSeverity,
)
from common.docker.exceptions import DockerContainerNotFoundError
from settings.config import OPENFAAS_IMAGE_NAME

from .openfaas_container_manager import OpenFaaSContainerManager


def pull_function_version(
    image_manager: ImageManager,
    repository: str,
    function: str,
    version: str,
) -> None:
    image_tag = image_manager.format_function_tag(function, version)

    image_manager.pull(
        repository,
        image_tag,
    )


class FaaSStop(Command):
    name = "stop"

    short_help = "Stop the running OpenFaaS service.."

    help = """
'das-cli faas stop' allows you to stop the execution of the DAS function in
OpenFaaS. This is useful for terminating the function's operation when it's no
longer needed. After stopping the faas, the function will no longer be
available and cannot be used with the DAS.

.SH EXAMPLES

This is an example of how to stop the function

$ das-cli faas stop
"""

    @inject
    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self._settings = settings

    def run(self):
        self._settings.raise_on_missing_file()
        self._settings.raise_on_schema_mismatch()

        self.stdout("Stopping OpenFaaS service...")

        openfaas_container_name = self._settings.get("services.openfaas.container_name")

        try:
            openfaas_container_service = OpenFaaSContainerManager(openfaas_container_name)
            openfaas_container_service.stop()

            self.stdout("OpenFaaS service stopped", severity=StdoutSeverity.SUCCESS)
        except DockerContainerNotFoundError:
            self.stdout("FaaS is not running...", severity=StdoutSeverity.WARNING)


class FaaSStart(Command):
    name = "start"

    short_help = "Start OpenFaaS service."

    help = r"""
OpenFaaS, an open-source serverless computing platform, makes running functions
in containers fast and simple. With this command, you can initialize the DAS
remotely through a function in OpenFaaS, which can be run on your server or
locally.

If you've just installed the DAS CLI, the function will be executed using the
latest version by default. However, if you want to specify a particular
version, you can use the faas update-version command. Versions are available at
https://github.com/singnet/das-serverless-functions/releases, or you can choose
to leave it as latest, which will always use the latest available version.

Since the function needs to communicate with databases, you need to run db
start to establish this communication. Upon the first execution of the
function, it might take a little longer as it needs to fetch the specified
version and set everything up for you. Subsequent initializations will be
faster unless you change the version, which will require the same process again
to set everything up.

.B
Ensure that the following ports are open:

.IP \[bu] 2
Port 8080: For the function

.IP \[bu] 2
Port 8081: For metrics

.IP \[bu] 2
Port 5000: For the watchdog

After starting the function, you will receive a message on the screen with the
function version and the port on which the function is being executed.

.SH EXAMPLES

This is an example of how to start the function.

$ das-cli faas start
"""

    @inject
    def __init__(
        self,
        settings: Settings,
        image_manager: ImageManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._image_manager = image_manager

    def _is_required_services_running(self, services: list):
        services_not_running = False

        for service in services:
            container_manager = service["container_manager"]
            service_name = service["name"]
            service_port = service["port"]

            if not container_manager.is_running():
                self.stdout(
                    f"{service_name} is not running",
                    severity=StdoutSeverity.ERROR,
                )
                services_not_running = True
            else:
                self.stdout(
                    f"{service_name} is running on port {service_port}",
                    severity=StdoutSeverity.WARNING,
                )

        if services_not_running:
            raise DockerContainerNotFoundError(
                "\nPlease use 'db start' to start required services before running 'faas start'."
            )

    def run(self):
        self._settings.raise_on_missing_file()
        self._settings.raise_on_schema_mismatch()

        redis_container_name = self._settings.get("services.redis.container_name")
        redis_port = self._settings.get("services.redis.port")

        mongodb_container_name = self._settings.get("services.mongodb.container_name")
        mongodb_port = self._settings.get("services.mongodb.port")
        mongodb_username = self._settings.get("services.mongodb.username")
        mongodb_password = self._settings.get("services.mongodb.password")

        self._is_required_services_running(
            [
                {
                    "name": "MongoDB",
                    "container_manager": MongodbContainerManager(mongodb_container_name),
                    "port": mongodb_port,
                },
                {
                    "name": "Redis",
                    "container_manager": RedisContainerManager(redis_container_name),
                    "port": redis_port,
                },
            ]
        )

        self.stdout("Starting OpenFaaS...")

        function = self._settings.get("services.openfaas.function")
        version = self._settings.get("services.openfaas.version")

        pull_function_version(
            self._image_manager,
            OPENFAAS_IMAGE_NAME,
            function,
            version,
        )

        openfaas_container_name = self._settings.get("services.openfaas.container_name")

        openfaas_container_manager = OpenFaaSContainerManager(openfaas_container_name)

        function_version = self._image_manager.format_function_tag(function, version)

        openfaas_container_manager.start_container(
            function_version,
            redis_port,
            mongodb_port,
            mongodb_username,
            mongodb_password,
        )

        label = openfaas_container_manager.get_label("fn.version") or version
        version_str = f"latest ({label})" if version == "latest" else label

        self.stdout(
            f"You are running the version '{version_str}' of the function.\nOpenFaaS running on port 8080",
            severity=StdoutSeverity.SUCCESS,
        )


class FaaSRestart(Command):
    name = "restart"

    short_help = "Restart OpenFaaS service."

    help = """
'das-cli faas restart' restarts OpenFaaS server container. This is useful when
you want to restart the function to apply configuration changes. During this
process, there is typically a downtime until the function is running again and
deemed healthy. This downtime occurs because the existing instance of the
function needs to be stopped, and then a new instance needs to be started with
the updated configuration or changes.

.SH EXAMPLES

This is an example of how to restart the execution of the faas function.

$ das-cli faas restart
"""

    @inject
    def __init__(self, faas_start: FaaSStart, faas_stop: FaaSStop) -> None:
        super().__init__()
        self._faas_start = faas_start
        self._faas_stop = faas_stop

    def run(self):
        self._faas_stop.run()
        self._faas_start.run()


class FaaSVersion(Command):
    name = "version"

    short_help = "Get OpenFaaS function version."

    help = """
'das-cli faas version' is used to display the current version of the DAS
function in OpenFaaS. This command is particularly useful for checking the
version of the deployed function, which can be helpful troubleshooting issues,
or ensuring compatibility.

.SH EXAMPLES

This is an example illustrating how to retrieve the version of the function.

$ das-cli faas version
"""

    @inject
    def __init__(
        self,
        settings: Settings,
        image_manager: ImageManager,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._image_manager = image_manager

    def get_current_function_version(self) -> tuple:
        self._settings.rewind()  # Ensure we are getting the latest setting content
        function = self._settings.get("services.openfaas.function", "query-engine")

        image_tag = self._image_manager.get_label(
            repository=OPENFAAS_IMAGE_NAME,
            tag=self._image_manager.format_function_tag(
                function,
                version=self._settings.get("services.openfaas.version", "latest"),
            ),
            label="fn.version",
        )

        assert image_tag is not None, "Image tag is None"

        version = image_tag.split("-").pop()

        return function, version

    def run(self):
        self._settings.raise_on_missing_file()
        self._settings.raise_on_schema_mismatch()

        function, version = self.get_current_function_version()

        self.stdout(f"{function} {version}", severity=StdoutSeverity.SUCCESS)


class FaaSUpdateVersion(Command):
    name = "update-version"

    short_help = "Update an OpenFaaS service to a newer version."

    help = """
'das-cli update-version' allows you to update the version of your function in
OpenFaaS. All available versions can be found at
https://github.com/singnet/das-serverless-functions/releases. This command has
two optional parameters. When executed without parameters, it will fetch the
latest version of the 'query-engine' function and update it on your local
server if a newer version is found. You can also specify the function you want
to update in OpenFaaS (currently only 'query-engine' is available), and define
the version of the function you want to use, as mentioned earlier.

.SH EXAMPLES

This is an example of how to update to the latest available function version.

$ das-cli update-version

This is an example of how to update the function you want to use (currently only `query-engine` is available).

$ das-cli update-version --function query-engine

This demonstrates updating the function version to a specific release. You need to specify the version in the semver format

$ das-cli update-version --version 1.0.0
"""

    params = [
        CommandOption(
            ["--version", "-v"],
            help="Specify the version of the OpenFaaS function (format: x.x.x).",
            required=False,
            type=FunctionVersion(),
            default="latest",
        ),
        CommandOption(
            ["--function", "-fn"],
            help="Specify the OpenFaaS function to start.",
            required=False,
            type=Choice(["query-engine"]),
            default="query-engine",
        ),
    ]

    @inject
    def __init__(
        self,
        settings: Settings,
        image_manager: ImageManager,
        faas_version: FaaSVersion,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._image_manager = image_manager
        self._faas_version = faas_version

    def _set_version(self, function: str, version: str) -> None:
        self._settings.set("services.openfaas.version", version)
        self._settings.set("services.openfaas.function", function)
        self._settings.save()
        self._settings.rewind()

    def run(
        self,
        version: str,
        function: str,
    ) -> None:
        self._settings.raise_on_missing_file()
        self._settings.raise_on_schema_mismatch()

        (
            current_function_name,
            current_function_version,
        ) = self._faas_version.get_current_function_version()

        self.stdout(f"Downloading the {function} function, version {version}...")

        pull_function_version(
            self._image_manager,
            OPENFAAS_IMAGE_NAME,
            function,
            version,
        )

        self._set_version(function, version)

        (
            newer_function_name,
            newer_function_version,
        ) = self._faas_version.get_current_function_version()

        if (
            current_function_name != newer_function_name
            or current_function_version != newer_function_version
        ):
            self.stdout(
                f"Function version successfully updated {current_function_name} {current_function_version} --> {newer_function_name} {newer_function_version}. You need to call 'faas restart' to start using the new version.",
                severity=StdoutSeverity.SUCCESS,
            )
        else:
            self.stdout(
                f"Function {current_function_name} is already at version {current_function_version}",
                severity=StdoutSeverity.WARNING,
            )


class FaaSCli(CommandGroup):
    name = "faas"

    short_help = "Manage OpenFaaS services."

    help = "'das-cli faas' provides management commands for OpenFaaS using the DAS CLI including deployment of latest or specific versions, service start/stop/restart, among others."

    @inject
    def __init__(
        self,
        faas_start: FaaSStart,
        faas_stop: FaaSStop,
        faas_restart: FaaSRestart,
        faas_version: FaaSVersion,
        faas_update_version: FaaSUpdateVersion,
    ) -> None:
        super().__init__()
        self.add_commands(
            [
                faas_start.command,
                faas_stop.command,
                faas_restart.command,
                faas_version.command,
                faas_update_version.command,
            ]
        )
