import os
import sys

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
    DasPackageUpdateError,
    DasNotFoundError,
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
    def __init__(self) -> None:
        super().__init__()
        self.package_dir = sys.executable
        self.package_name = "das-toolbox"
        self._das_ubuntu_apt_tool = DasUbuntuAdvancedPackagingTool(self.package_name)

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

        current_version = self._das_ubuntu_apt_tool.get_package_version()

        if not is_binary and not current_version:
            raise DasNotFoundError(
                f"The package {self.package_name} can only be updated if you installed it via apt."
            )

        try:
            self.stdout(f"Updating the package {self.package_name}...")
            newer_version = self._das_ubuntu_apt_tool.install_package(version)
        except Exception as e:
            raise DasPackageUpdateError(
                f"The package '{self.package_name}' could not be updated. Reason: {str(e)}"
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
        self.version()
        self.add_commands(
            [
                das_cli_update_version,
            ]
        )

    def version(self) -> None:
        self.group = click.version_option(VERSION, message="%(prog)s %(version)s")(self.group)
