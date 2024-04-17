import click
import pkg_resources
import requests
from exceptions import NotFound
import subprocess
import re
from enum import Enum


class LibraryEnum(Enum):
    HYPERON_DAS = "hyperon-das"
    HYPERON_DAS_ATOMDB = "hyperon-das-atomdb"


@click.group()
@click.pass_context
def python_library(ctx):
    """
    Manage versions of Python libraries.

    'das-cli python-library' allows you to manage versions of DAS Python libraries, such as hyperon-das and hyperon-das-atomdb.
    This tool provides commands to list available versions, set specific versions, update to the latest versions, and display installed versions of Python libraries.
    """

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

    try:
        subprocess.run(
            ["python", "-m", "pip", "install", "--upgrade", "--quiet", pypi_package],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
    except subprocess.CalledProcessError:
        raise Exception(
            f"Failed to update package {package_name}. Please verify if the provided version exists or ensure the package name is correct."
        )


def print_package_info(package_name, current_version, latest_version):
    click.echo(
        f"{package_name}\n"
        f"  INSTALLED: {current_version}\n"
        f"  LATEST:    {latest_version}"
    )


def validate_version(version):
    if not re.match(r"v?\d+\.\d+\.\d+", version):
        click.secho("The version must follow the format x.x.x (e.g 1.10.9)", fg="red")
        exit(1)


def extract_versions(versions, show_patches=False):
    filtered_versions = set()
    for version in versions:
        if show_patches:
            filtered_versions.add(version)
        else:
            match = re.match(r"^(\d+\.\d+)", version)
            if match:
                filtered_versions.add(match.group(1))
    return sorted(filtered_versions)


def get_all_versions_from_pypi(package_name):
    response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
    if response.status_code == 200:
        data = response.json()
        return list(data["releases"].keys())
    return []


def get_all_major_minor_versions_from_pypi(package_name, show_patches=False):
    all_versions = get_all_versions_from_pypi(package_name)
    return extract_versions(all_versions, show_patches)


def print_versions(versions):
    max_length = max(len(version) for version in versions)
    num_columns = min(5, len(versions))
    column_width = max_length + 2
    num_rows = -(-len(versions) // num_columns)
    for row in range(num_rows):
        line = ""
        for col in range(num_columns):
            index = row + col * num_rows
            if index < len(versions):
                line += versions[index].ljust(column_width)
        click.echo(line)


@python_library.command()
def version():
    """
    Show currently installed and newest available versions of both, hyperon-das and hyperon-das-atomdb.

    'das-cli python-library version' displays the versions of installed DAS Python libraries, such as hyperon-das and hyperon-das-atomdb.

    .SH EXAMPLES

    Display versions of installed Python libraries.

    $ das-cli python-library version
    """
    packages = ["hyperon-das", "hyperon-das-atomdb"]

    try:
        for package in packages:
            current_version = get_python_package_version(package)
            latest_version = get_latest_python_package_version(package)
            print_package_info(package, current_version, latest_version)

    except Exception as e:
        click.secho(f"{str(e)}", fg="red")
        exit(1)


@python_library.command()
def update():
    """
    Update both hyperon-das and hyperon-das-atomdb to the newest available or to a specific version.

    'das-cli python-library update' updates the versions of Python libraries, such as hyperon-das and hyperon-das-atomdb, to the latest available versions.

    .SH EXAMPLES

    Update all Python libraries to their latest versions.

    $ das-cli python-library update
    """
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

    ctx = click.Context(python_library)
    ctx.invoke(version)


@python_library.command(name="set")
@click.option(
    "--hyperon-das",
    help="Set the version of the hyperon-das library to the specified version. Available versions can be found at https://github.com/singnet/das-query-engine/releases.",
    type=str,
    required=False,
)
@click.option(
    "--hyperon-das-atomdb",
    type=str,
    help="Set the version of the hyperon-das-atomdb library to the specified version. Available versions can be found at https://github.com/singnet/das-atom-db/releases.",
    required=False,
)
def set_versions(hyperon_das, hyperon_das_atomdb):
    """
    Allow setting specific versions for both hyperon-das and hyperon-das-atomdb libraries

    'das-cli python-library set' sets the versions of Python libraries, such as hyperon-das and hyperon-das-atomdb, to the specified versions.
    This command requires at least one of the following parameters: --hyperon-das or --hyperon-das-atomdb.

    .SH EXAMPLES

    Set the version of the hyperon-das library to version 1.2.0.

    $ das-cli python-library set --hyperon-das=1.2.0

    Set the version of the hyperon-das-atomdb library to version 0.4.0.

    $ das-cli python-library set --hyperon-das-atomdb=0.4.0
    """
    if hyperon_das is None and hyperon_das_atomdb is None:
        click.secho(
            "At least one of --hyperon-das or --hyperon-das-atomdb must be provided.",
            fg="red",
        )
        exit(1)

    packages = {
        "hyperon-das": hyperon_das,
        "hyperon-das-atomdb": hyperon_das_atomdb,
    }

    for package_name, package_version in packages.items():
        if package_version is not None:
            try:
                validate_version(package_version)
                click.echo(f"Updating package {package_name}...")
                update_python_package_version(package_name, version=package_version)
                click.secho(
                    f"Package {package_name} has been successfully updated.",
                    fg="green",
                )
            except NotFound as e:
                click.secho(str(e), fg="red")
                exit(1)
            except Exception as e:
                click.secho(
                    f"An error occurred while trying to update {package_name}: {str(e)}",
                    fg="red",
                )
                exit(1)

    ctx = click.get_current_context()
    ctx.invoke(version)


@python_library.command(name="list")
@click.option(
    "--show-patches",
    is_flag=True,
    help="Include patch versions in the list of available versions.",
    required=False,
)
@click.option(
    "--library",
    help="Specify the name of the library to filter the list of available versions.",
    required=False,
    type=click.Choice([e.value for e in LibraryEnum]),
)
def list_versions(show_patches, library):
    """
    List all major/minor versions of hyperon-das and hyperon-das-atomdb.

    'das-cli python-library list' lists available versions of DAS Python libraries, such as hyperon-das and hyperon-das-atomdb, from the PyPI.
    By default, it displays all major and minor versions of both hyperon-das and hyperon-das-atomdb libraries.

    .SH EXAMPLES

    List all major and minor versions of hyperon-das and hyperon-das-atomdb.

    $ das-cli python-library list

    List all major and minor versions of the hyperon-das library.

    $ das-cli python-library list --library hyperon-das

    List all major, minor, and patch versions.

    $ das-cli python-library list --show-patches
    """

    packages = [
        "hyperon-das",
        "hyperon-das-atomdb",
    ]

    for package in packages:
        if library is not None and package != library:
            continue

        versions = get_all_major_minor_versions_from_pypi(package, show_patches)
        click.secho(f"\n{package} available versions:\n", fg="green")
        print_versions(versions)
