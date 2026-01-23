import os
import sys

import click
import distro
from injector import inject

from common import Command, CommandGroup, CommandOption, StdoutSeverity, is_executable_bin
from settings.config import VERSION

from .das_cli_docs import HELP_DAS_CLI, HELP_UPD_VERSION, SHORT_HELP_DAS_CLI, SHORT_HELP_UPD_VERSION
from .das_ubuntu_advanced_packaging_tool import (
    DasNotFoundError,
    DasPackageUpdateError,
    DasUbuntuAdvancedPackagingTool,
)


class PermissionError(Exception): ...  # noqa: E701


class DasCliUpdateVersion(Command):
    name = "update-version"

    short_help = SHORT_HELP_UPD_VERSION

    help = HELP_UPD_VERSION

    @inject
    def __init__(self, das_ubuntu_advanced_packaging_tool: DasUbuntuAdvancedPackagingTool) -> None:
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

    def _check_is_executable(self):
        is_executable = is_executable_bin()

        if not is_executable:
            raise PermissionError(
                "This command should be executed as an executable rather than as a Python script."
            )

    def _check_linux_distro(self):
        if distro.id() != "ubuntu":
            self.stdout(
                "It's advisable to utilize this command specifically for Ubuntu distributions.",
                severity=StdoutSeverity.WARNING,
            )

    def _check_sudo_permission(self):
        is_sudo = "SUDO_USER" in os.environ

        if not is_sudo:
            raise PermissionError("Requires 'root' permissions to execute")

    def _check_installed_via_apt(self):
        installed_version = self._das_ubuntu_advanced_packaging_tool.get_package_version()

        if installed_version is None:
            raise DasNotFoundError(
                f"The package '{self._das_ubuntu_advanced_packaging_tool.package_name}' is not installed via APT."
            )

        return installed_version

    def _check_cli_version(self, current_version, newer_version):

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

    def run(self, version):

        self._check_is_executable()
        self._check_sudo_permission()
        self._check_linux_distro()
        self._check_installed_via_apt()

        current_version = self._das_ubuntu_advanced_packaging_tool.get_package_version()

        try:
            self.stdout(
                f"Updating the package {self._das_ubuntu_advanced_packaging_tool.package_name}..."
            )
            newer_version = self._das_ubuntu_advanced_packaging_tool.install_package(version)

        except Exception as e:
            raise DasPackageUpdateError(
                f"The package '{self._das_ubuntu_advanced_packaging_tool.package_name}' could not be updated. Reason: {str(e)}"
            ) from e

        self._check_cli_version(current_version, newer_version)


class DasCli(CommandGroup):
    name = "das-cli"

    short_help = SHORT_HELP_DAS_CLI
    help = HELP_DAS_CLI

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
