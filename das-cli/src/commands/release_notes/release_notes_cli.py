from typing import List

from injector import inject

from common import CommandGroup, CommandOption, RegexType, StdoutSeverity

from .release_notes_package import Library, ReleaseNotesPackage

from .release_notes_docs import *

class ReleaseNotesCli(CommandGroup):
    name = "release-notes"

    aliases = ["rn"]

    short_help = SHORT_HELP_RELEASE_NOTES

    help = HELP_RELEASE_NOTES

    params = [
        CommandOption(
            ["--module"],
            type=RegexType(r"(\w+)=(\w+)", "Input does not match a valid module name"),
            help="Specify the name of the module to view release notes for a specific component of DAS.",
            required=False,
        ),
        CommandOption(
            ["--list"],
            is_flag=True,
            help="Display only a list of available versions for each component without displaying the changelog.",
            required=False,
        ),
    ]

    @inject
    def __init__(
        self,
        release_notes_package: ReleaseNotesPackage,
    ) -> None:
        super().__init__()
        self.override_group_command()
        self._release_notes_package = release_notes_package

    def run(
        self,
        module,
        list,
    ):
        releases: List[Library] = []

        if not module:
            releases = self._release_notes_package.get_latest_release_notes()
        else:
            releases = self._release_notes_package.get_release_notes(module)

        for package in releases:
            package_name = package.get_name()
            package_version = package.get_version()

            self.stdout(
                f"\n{package_name}: {package_version}",
                severity=StdoutSeverity.SUCCESS,
            )

            if not list:
                changelog = package.get_changelog()
                self.stdout(f"\n{changelog}")
