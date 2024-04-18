import click
from sys import exit
from commands import (
    config,
    db,
    faas,
    metta,
    example,
    logs,
    jupyter_notebook,
    python_library,
    release_notes,
)
from config import Secret, SECRETS_PATH, USER_DAS_PATH, VERSION
from services import UbuntuAdvancedPackagingToolService
from exceptions import NotFound
import distro
import os
import sys


@click.group()
@click.version_option(VERSION, message="%(prog)s %(version)s")
@click.pass_context
def das_cli(ctx):
    ctx.ensure_object(dict)

    try:
        ctx.obj["config"] = Secret()
    except PermissionError:
        click.secho(
            f"\nIt seems that you don't have the required permissions to write to {SECRETS_PATH}.\n\nTo resolve this, please make sure you are the owner of the file by running: `sudo chown $USER:$USER {USER_DAS_PATH} -R`, and then grant the necessary permissions using: `sudo chmod 770 {USER_DAS_PATH} -R`\n",
            fg="red",
        )
        exit(1)


@das_cli.command(help="Update Package Version.")
@click.option(
    "--version",
    help="Specify the version of the package (format: x.x.x).",
    required=False,
    type=str,
    default=None,
)
def update_version(version):
    is_executable = getattr(sys, "frozen", False)

    if distro.id() != "ubuntu" or not is_executable:
        click.secho("This command can only be used on Ubuntu.", fg="red")
        exit(1)

    package_dir = sys.executable
    package_name = os.path.basename(package_dir)

    is_sudo = "SUDO_USER" in os.environ

    if not is_sudo:
        click.secho("This command is not being executed with sudo.", fg="red")
        exit(1)

    ubuntu_apt_service = UbuntuAdvancedPackagingToolService(package_name)

    try:
        is_binary = os.access(
            package_dir,
            os.X_OK,
        )

        current_version, _ = ubuntu_apt_service.get_package_version()

        if not is_binary and not current_version:
            raise NotFound()

    except NotFound:
        click.secho(
            f"The package {package_name} can only be updated if you installed it via apt.",
            fg="red",
        )
        exit(1)

    try:
        click.echo(f"Updating the package {package_name}...")
        newer_version = ubuntu_apt_service.install_package(version)
    except Exception:
        click.secho(
            f"The {package_name} could not be updated. Please check if the specified version exists.",
            fg="red",
        )
        exit(1)

    if current_version != newer_version:
        click.secho(
            f"Package version successfully updated  {current_version} --> {newer_version}.",
            fg="green",
        )
    else:
        click.secho(
            f"The package is already updated to version {newer_version}.",
            fg="yellow",
        )


das_cli.add_command(config)
das_cli.add_command(db)
das_cli.add_command(faas)
das_cli.add_command(metta)
das_cli.add_command(example)
das_cli.add_command(logs)
das_cli.add_command(jupyter_notebook)
das_cli.add_command(python_library)
das_cli.add_command(release_notes)

if __name__ == "__main__":
    das_cli()
