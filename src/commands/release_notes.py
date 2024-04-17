import click
from services import ReleaseNotesService
from exceptions import NotFound


@click.command()
@click.option(
    "--module",
    type=str,
    help="Specify the name of the module to view release notes for a specific component of DAS.",
    required=False,
)
@click.option(
    "--list",
    "is_list",
    is_flag=True,
    help="Display only a list of available versions for each component without displaying the changelog.",
    required=False,
)
def release_notes(module, is_list):
    """
    Display available release notes.

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
    releases = []
    release_notes_service = ReleaseNotesService()

    if not module:
        releases = release_notes_service.get_latest_release_notes()
    else:
        try:
            releases = release_notes_service.get_release_notes(module)
        except NotFound:
            click.secho(
                f"Module '{module}' not found. Please make sure the module name or module version is correct.",
                fg="red",
            )
            exit(1)

    for package in releases:
        package_name = package.get_name()
        package_version = package.get_version()

        click.secho(f"\n{package_name}: {package_version}", fg="green")

        if not is_list:
            changelog = package.get_changelog()
            click.echo(f"\n{changelog}")
