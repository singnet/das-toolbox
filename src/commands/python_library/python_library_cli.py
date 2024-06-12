from enum import Enum
from injector import inject
from common import (
    Command,
    CommandGroup,
    CommandOption,
    Choice,
    StdoutSeverity,
    FunctionVersion,
)
from .python_library_package import PythonLibraryPackage, PackageError


class LibraryEnum(Enum):
    HYPERON_DAS = "hyperon-das"
    HYPERON_DAS_ATOMDB = "hyperon-das-atomdb"


class PythonLibraryVersion(Command):
    name = "version"

    short_help = "Show currently installed and newest available versions of both, hyperon-das and hyperon-das-atomdb."

    help = """
'das-cli python-library version' displays the versions of installed DAS Python libraries, such as hyperon-das and hyperon-das-atomdb.

.SH EXAMPLES

Display versions of installed Python libraries.

$ das-cli python-library version
"""

    packages = ["hyperon-das", "hyperon-das-atomdb"]

    @inject
    def __init__(self, python_library_package: PythonLibraryPackage) -> None:
        super().__init__()
        self._python_library_package = python_library_package

    def get_packages_version(self) -> list:
        packages_versions = []

        for package in self.packages:
            current_version = self._python_library_package.get_version(package)
            latest_version = self._python_library_package.get_latest_version(package)
            packages_versions.append((package, current_version, latest_version))

        return packages_versions

    def run(self):
        for package, current_version, latest_version in self.get_packages_version():
            self.stdout(
                f"{package}\n  INSTALLED: {current_version}\n  LATEST:    {latest_version}"
            )


class PythonLibraryList(Command):
    name = "list"

    short_help = "List all major/minor versions of hyperon-das and hyperon-das-atomdb."

    help = """
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

    params = [
        CommandOption(
            ["--show-patches", "-p"],
            is_flag=True,
            help="Include patch versions in the list of available versions.",
            required=False,
        ),
        CommandOption(
            ["--library", "-l"],
            help="Specify the name of the library to filter the list of available versions.",
            required=False,
            type=Choice([e.value for e in LibraryEnum]),
        ),
    ]

    @inject
    def __init__(self, python_library_package: PythonLibraryPackage) -> None:
        super().__init__()
        self._python_library_package = python_library_package

    def print_versions(self, versions):
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
            self.stdout(line)

    def run(self, show_patches, library):
        packages = [
            "hyperon-das",
            "hyperon-das-atomdb",
        ]

        for package in packages:
            if library is not None and package != library:
                continue

            versions = (
                self._python_library_package.get_all_major_minor_versions_from_pypi(
                    package,
                    show_patches,
                )
            )
            self.stdout(
                f"\n{package} available versions:\n",
                severity=StdoutSeverity.SUCCESS,
            )
            self.print_versions(versions)


class PythonLibrarySet(Command):
    name = "set"

    short_help = "Allow setting specific versions for both hyperon-das and hyperon-das-atomdb libraries"

    help = """
'das-cli python-library set' sets the versions of Python libraries, such as hyperon-das and hyperon-das-atomdb, to the specified versions.
This command requires at least one of the following parameters: --hyperon-das or --hyperon-das-atomdb.

.SH EXAMPLES

Set the version of the hyperon-das library to version 1.2.0.

$ das-cli python-library set --hyperon-das=1.2.0

Set the version of the hyperon-das-atomdb library to version 0.4.0.

$ das-cli python-library set --hyperon-das-atomdb=0.4.0
"""

    params = [
        CommandOption(
            ["--hyperon-das"],
            help="Set the version of the hyperon-das library to the specified version. Available versions can be found at https://github.com/singnet/das-query-engine/releases.",
            type=FunctionVersion(),
            required=False,
        ),
        CommandOption(
            ["--hyperon-das-atomdb"],
            type=FunctionVersion(),
            help="Set the version of the hyperon-das-atomdb library to the specified version. Available versions can be found at https://github.com/singnet/das-atom-db/releases.",
            required=False,
        ),
    ]

    @inject
    def __init__(
        self,
        python_library_package: PythonLibraryPackage,
        python_library_version: PythonLibraryVersion,
    ) -> None:
        super().__init__()
        self._python_library_package = python_library_package
        self._python_library_version = python_library_version

    def run(self, hyperon_das, hyperon_das_atomdb):
        if hyperon_das is None and hyperon_das_atomdb is None:
            self.stdout(
                "At least one of --hyperon-das or --hyperon-das-atomdb must be provided.",
                severity=StdoutSeverity.ERROR,
            )
            return

        successful_updates = True

        packages = {
            "hyperon-das": hyperon_das,
            "hyperon-das-atomdb": hyperon_das_atomdb,
        }

        for package_name, package_version in packages.items():
            if package_version is not None:
                try:
                    self.stdout(f"Updating package {package_name}...")
                    self._python_library_package.update_version(
                        package_name, package_version
                    )
                    self.stdout(
                        f"Package {package_name} has been successfully updated.",
                        severity=StdoutSeverity.SUCCESS,
                    )
                except PackageError as e:
                    successful_updates = False
                    self.stdout(str(e), severity=StdoutSeverity.ERROR)

        if successful_updates:
            self.stdout(
                "All package has been successfully updated.",
                severity=StdoutSeverity.SUCCESS,
            )
            self._python_library_version.safe_run()
        else:
            self.stdout(
                "One or more packages could not be updated.",
                severity=StdoutSeverity.ERROR,
            )


class PythonLibraryUpdate(Command):
    name = "update"

    short_help = "Update both hyperon-das and hyperon-das-atomdb to the newest available or to a specific version."

    help = """
'das-cli python-library update' updates the versions of Python libraries, such as hyperon-das and hyperon-das-atomdb, to the latest available versions.

.SH EXAMPLES

Update all Python libraries to their latest versions.

$ das-cli python-library update
"""

    packages = ["hyperon-das", "hyperon-das-atomdb"]

    @inject
    def __init__(
        self,
        python_library_package: PythonLibraryPackage,
        python_library_version: PythonLibraryVersion,
    ) -> None:
        super().__init__()
        self._python_library_package = python_library_package
        self._python_library_version = python_library_version

    def run(self):
        successful_updates = True

        for package in self.packages:
            try:
                self.stdout(f"Updating package {package}...")
                self._python_library_package.update_version(package)
            except PackageError as e:
                successful_updates = False
                self.stdout(str(e), severity=StdoutSeverity.ERROR)

        if successful_updates:
            self.stdout(
                "All package has been successfully updated.",
                severity=StdoutSeverity.SUCCESS,
            )
            self._python_library_version.safe_run()
        else:
            self.stdout(
                "One or more packages could not be updated.",
                severity=StdoutSeverity.ERROR,
            )


class PythonLibraryCli(CommandGroup):
    name = "python-library"

    short_help = "Manage versions of Python libraries."

    help = """
'das-cli python-library' allows you to manage versions of DAS Python libraries, such as hyperon-das and hyperon-das-atomdb.
This tool provides commands to list available versions, set specific versions, update to the latest versions, and display installed versions of Python libraries.
"""

    @inject
    def __init__(
        self,
        python_library_list: PythonLibraryList,
        python_library_set: PythonLibrarySet,
        python_library_update: PythonLibraryUpdate,
        python_library_version: PythonLibraryVersion,
    ) -> None:
        super().__init__()
        self.add_commands(
            [
                python_library_list.command,
                python_library_set.command,
                python_library_update.command,
                python_library_version.command,
            ]
        )
