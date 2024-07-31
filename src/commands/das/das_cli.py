import os
import click
import distro
import sys
from config import VERSION
from injector import inject
from common import (
    Command,
    CommandGroup,
    CommandOption,
    is_executable_bin,
    StdoutSeverity,
)
from .das_ubuntu_advanced_packaging_tool import (
    DasUbuntuAdvancedPackagingTool,
    DasNotFoundError,
    DasError,
)


class PermissionError(Exception): ...


class DasCliUpdateVersion(Command):
    name = "update-version"

    short_help = "Update the DAS CLI version (Ubuntu only)."

    help = """
'das-cli update-version' allows you to update the DAS CLI to the latest version available via the APT repository.
This command is intended for Ubuntu Linux distributions only and must be run with sudo privileges.

.SH EXAMPLES

Update the DAS CLI to the latest version available via APT repository.

$ sudo das-cli update-version

Update the DAS CLI to a specific version (e.g. 1.2.3) available via APT repository.

$ sudo das-cli update-version --version=1.2.3
"""

    @inject
    def __init__(self) -> None:
        super().__init__()
        self.package_dir = sys.executable
        self.package_name = os.path.basename(self.package_dir)
        self._das_ubuntu_apt_tool = DasUbuntuAdvancedPackagingTool(self.package_name)

    params = [
        CommandOption(
            ["--version", "-v"],
            help="Specify the version of the package (format: x.x.x).",
            required=False,
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

        current_version, _ = self._das_ubuntu_apt_tool.get_package_version()

        if not is_binary and not current_version:
            raise DasNotFoundError(
                f"The package {self.package_name} can only be updated if you installed it via apt."
            )

        try:
            self.stdout(f"Updating the package {self.package_name}...")
            newer_version = self._das_ubuntu_apt_tool.install_package(version)
        except Exception:
            raise DasError(
                f"The {self.package_name} could not be updated. Please check if the specified version exists."
            )

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

    help = "'das-cli' offers a suite of commands to efficiently manage a wide range of tasks including management of containerized services, OpenFaaS functions, knowledge base operations, and more."

    @inject
    def __init__(
        self,
        das_cli_update_version: DasCliUpdateVersion,
    ) -> None:
        super().__init__()
        self.version()
        self.add_commands(
            [
                das_cli_update_version.command,
            ]
        )

    def version(self):
        self.group = click.version_option(VERSION, message="%(prog)s %(version)s")(
            self.group
        )
