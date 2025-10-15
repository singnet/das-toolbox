import os
import sys
from common.execution_context import ExecutionContext
from common.utils import log_exception

import click
import distro
from injector import inject

from common import (
    Command,
    CommandGroup,
    CommandOption,
    StdoutSeverity,
    is_executable_bin,
)
from settings.config import VERSION

from .das_ubuntu_advanced_packaging_tool import (
    DasNotFoundError,
    DasPackageUpdateError,
    DasUbuntuAdvancedPackagingTool,
)


class PermissionError(Exception): ...  # noqa: E701


class DasCliUpdateVersion(Command):
    name = "update-version"

    short_help = "Update the DAS CLI version (Ubuntu only)."

    help = """
NAME

update-version - Update the DAS CLI version (Ubuntu only)

DESCRIPTION

This command updates the DAS CLI to the latest version available via the APT repository.
It is intended for Ubuntu Linux distributions only and must be run with sudo privileges.

.SH OPTIONS
--version, -v     Specify the version of the package to install (format: x.y.z).
                  If omitted, the latest available version will be installed.

REQUIREMENTS

- Must be executed as a compiled binary, not as a Python script.
- Requires root privileges (sudo).
- The CLI must have been installed via APT.

EXAMPLES

Update the DAS CLI to the latest version available via APT:

    $ sudo das-cli update-version

Update the DAS CLI to a specific version (e.g. 1.2.3):

    $ sudo das-cli update-version --version=1.2.3
"""

    @inject
    def __init__(
        self, das_ubuntu_advanced_packaging_tool: DasUbuntuAdvancedPackagingTool
    ) -> None:
        super().__init__()
        self.package_dir = sys.executable
        self._das_ubuntu_advanced_packaging_tool = das_ubuntu_advanced_packaging_tool

    params = [
        CommandOption(
            ["--version", "-v"],
            help="Specify the version of the package (format: x.x.x).",
            type=str,
            default=None,
        )
    ]

    def run(self, version):
        is_executable = is_executable_bin()

        if not is_executable:
            raise PermissionError(
                "This command should be executed as an executable rather than as a Python script."
            )

        if distro.id() != "ubuntu":
            self.stdout(
                "It's advisable to utilize this command specifically for Ubuntu distributions.",
                severity=StdoutSeverity.WARNING,
            )

        is_sudo = "SUDO_USER" in os.environ

        if not is_sudo:
            raise PermissionError("Requires 'root' permissions to execute")

        is_binary = os.access(
            self.package_dir,
            os.X_OK,
        )

        current_version = self._das_ubuntu_advanced_packaging_tool.get_package_version()

        if not is_binary and not current_version:
            raise DasNotFoundError(
                f"The package {self._das_ubuntu_advanced_packaging_tool.package_name} can only be updated if you installed it via apt."
            )

        try:
            self.stdout(
                f"Updating the package {self._das_ubuntu_advanced_packaging_tool.package_name}..."
            )
            newer_version = self._das_ubuntu_advanced_packaging_tool.install_package(
                version
            )
        except Exception as e:
            raise DasPackageUpdateError(
                f"The package '{self._das_ubuntu_advanced_packaging_tool.package_name}' could not be updated. Reason: {str(e)}"
            ) from e

        if current_version != newer_version:
            self.stdout(
                f"Package version successfully updated  {current_version} --> {newer_version}.",
                severity=StdoutSeverity.SUCCESS,
            )
        else:
            self.stdout(
                f"The package is already updated to version {newer_version}.",
                severity=StdoutSeverity.WARNING,
            )


class DasCli(CommandGroup):
    name = "das-cli"

    short_help = "'das-cli' offers a suite of commands to efficiently manage a wide range of tasks including management of containerized services"

    help = """
NAME

das-cli - Command-line interface for managing DAS services

DESCRIPTION

'das-cli' offers a suite of commands to efficiently manage a wide range of tasks, including:

- Containerized service orchestration
- OpenFaaS function management
- Knowledge base operations
- System package management (via APT)

REMOTE EXECUTION

Any command can be executed on a remote server via SSH by enabling the --remote flag and providing connection parameters.

OPTIONS FOR REMOTE EXECUTION

--remote              Run the command on a remote server over SSH
--host, -H            Hostname or IP address of the remote server
--user, -H            SSH login user
--port, -H            SSH port (default: 22)
--key-file            Path to the SSH private key file (for key-based authentication)
--password            SSH password (not recommended for production)
--connect-timeout     SSH connection timeout in seconds (default: 10)

EXAMPLES

Run command remotely using SSH key:

    $ das-cli deploy --remote --host 192.168.0.10 --user ubuntu --key-file ~/.ssh/id_rsa

Run command remotely using password:

    $ das-cli update --remote --host 10.0.0.2 --user root --password yourpassword

"""

    @inject
    def __init__(
        self,
        das_cli_update_version: DasCliUpdateVersion,
    ) -> None:
        super().__init__()
        self.with_execution_context()
        self.version()
        self.add_commands(
            [
                das_cli_update_version,
            ]
        )

    def version(self) -> None:
        self.group = click.version_option(VERSION, message="%(prog)s %(version)s")(
            self.group
        )

    def _build_execution_context_from_argv(self, argv=None):
        if argv is None:
            argv = sys.argv[1:]

        def get_arg_value(name, default=None):
            if name in argv:
                idx = argv.index(name)
                if idx + 1 < len(argv):
                    return argv[idx + 1]
            return default

        remote_host = get_arg_value("--host")
        remote_port = int(get_arg_value("--port", 22))
        remote_user = get_arg_value("--user")
        remote_password = get_arg_value("--password")
        remote_key_path = get_arg_value("--key-file")
        remote_connection_timeout = int(get_arg_value("--connect-timeout", 10))
        context_json = get_arg_value("--context")

        return ExecutionContext(
            remote_host=remote_host,
            remote_port=remote_port,
            remote_user=remote_user,
            remote_key_path=remote_key_path,
            remote_password=remote_password,
            remote_connection_timeout=remote_connection_timeout,
            context_str=context_json,
        )

    def with_execution_context(self):
        original_callback = self.group.callback

        @click.pass_context
        def callback(ctx, *args, **kwargs):
            ctx.ensure_object(dict)
            try:
                ctx.obj["execution_context"] = self._build_execution_context_from_argv()
            except Exception as e:
                log_exception(e)
                sys.exit(1)

            if original_callback:
                return ctx.invoke(original_callback, *args, **kwargs)

        self.group.callback = callback

