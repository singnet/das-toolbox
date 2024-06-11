from injector import inject
from common import CommandOption, CommandGroup, StdoutSeverity
from .release_notes_package import ReleaseNotesPackage


class ReleaseNotesCli(CommandGroup):
    name = "release-notes"

    short_help = "Display available release notes."

    help = """
'das-cli release-notes' allows you to view release notes for DAS.
This command retrieves information from the release notes document hosted at https://github.com/singnet/das/blob/master/docs/release-notes.md.
It displays the release notes for the latest DAS' version available.

.SH EXAMPLES

View release notes for the latest DAS' version.

$ das-cli release-notes

View release notes for the hyperon-das component.

$ das-cli release-notes --module=hyperon-das

View a list of available versions for each component without displaying the full changelog.

$ das-cli release-notes --list
"""

    params = [
        CommandOption(
            ["--module"],
            type=str,
            help="Specify the name of the module to view release notes for a specific component of DAS.",
            required=False,
        ),
        CommandOption(
            ["--list"],
            "is_list",
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
        self.group.invoke = self.run
        self._release_notes_package = release_notes_package

    def run(
        self,
        ctx,
    ):
        module = ctx.params.get("module")
        is_list = ctx.params.get("list")
        releases = []

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

            if not is_list:
                changelog = package.get_changelog()
                self.stdout(f"\n{changelog}")
