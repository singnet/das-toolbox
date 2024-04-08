import click
from services import ReleaseNotesService
from exceptions import NotFound


@click.command(help="")
@click.option(
    "--module",
    type=str,
    help="Package or library module to get release notes for.",
    required=False,
)
@click.option(
    "--list",
    "is_list",
    is_flag=True,
    help="List available release notes versions.",
    required=False,
)
def release_notes(module, is_list):
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
