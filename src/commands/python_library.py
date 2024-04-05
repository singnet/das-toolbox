import click
import pkg_resources
import requests
from exceptions import NotFound
import subprocess


@click.group(help="")
@click.pass_context
def python_library(ctx):
    global config

    config = ctx.obj["config"]


def get_python_package_version(package_name):
    try:
        versao = pkg_resources.get_distribution(package_name).version
        return versao
    except pkg_resources.DistributionNotFound:
        raise NotFound(f"Package '{package_name}' is not installed.")


def get_latest_python_package_version(package_name):
    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data["info"]["version"]
    except requests.exceptions.RequestException as e:
        raise NotFound(
            f"Error while fetching the latest version of the package '{package_name}': {e}"
        )


def update_python_package_version(package_name, version=None):
    get_python_package_version(package_name)

    pypi_package = f"{package_name}=={version}" if version is not None else package_name

    subprocess.run(
        ["python", "-m", "pip", "install", "--upgrade", "--quiet", pypi_package],
        check=True,
    )


def print_package_info(package_name, current_version, latest_version):
    click.echo(
        f"{package_name}\n"
        f"  INSTALLED: {current_version}\n"
        f"  LATEST:    {latest_version}"
    )


@python_library.command(help="")
def version():
    packages = ["hyperon-das", "hyperon-das-atomdb"]

    try:
        for package in packages:
            current_version = get_python_package_version(package)
            latest_version = get_latest_python_package_version(package)
            print_package_info(package, current_version, latest_version)

    except Exception as e:
        click.secho(f"{str(e)}", fg="red")
        exit(1)


@python_library.command(help="")
def update():
    packages = ["hyperon-das", "hyperon-das-atomdb"]

    for package in packages:
        try:
            click.echo(f"Updating package {package}...")
            update_python_package_version(package)
        except NotFound as e:
            click.secho(f"{str(e)}", fg="red")
            exit(1)
        except Exception as e:
            click.secho(
                f"An error occurred while trying to update {package}: {str(e)}",
                fg="red",
            )
            exit(1)

    click.secho("All package has been successfully updated.", fg="green")

    ctx = click.get_current_context()
    ctx.invoke(version)
