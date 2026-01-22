HELP_LIB_VERSION = """
NAME

    python-library version - Display installed and latest available versions of DAS Python libraries.

SYNOPSIS

    das-cli python-library version

DESCRIPTION

    'das-cli python-library version' displays the versions of installed DAS Python libraries, such as hyperon-das and hyperon-das-atomdb.

EXAMPLES

Display versions of installed Python libraries.

    $ das-cli python-library version
"""

SHORT_HELP_LIB_VERSION = "Show currently installed and newest available versions of both, hyperon-das and hyperon-das-atomdb."

HELP_LIB_LIST = """
NAME

    python-library list - List available major and minor versions of DAS Python libraries.

SYNOPSIS

    das-cli python-library list [--show-patches] [--library <library_name>]

DESCRIPTION

    'das-cli python-library list' lists available versions of DAS Python libraries, such as hyperon-das and hyperon-das-atomdb, from PyPI.
    By default, it displays all major and minor versions of both libraries.

OPTIONS

--show-patches, -p

    Include patch versions in the list of available versions.

--library <library-name>, -l <library-name>

    Specify the name of the library to filter the list of available versions.
    Possible values: hyperon-das, hyperon-das-atomdb

EXAMPLES

    List all major and minor versions of hyperon-das and hyperon-das-atomdb.

    $ das-cli python-library list

    List all major and minor versions of the hyperon-das library.

    $ das-cli python-library list --library hyperon-das

    List all major, minor, and patch versions.

    $ das-cli python-library list --show-patches
"""

SHORT_HELP_LIB_LIST = "List all major/minor versions of hyperon-das and hyperon-das-atomdb."

HELP_LIB_SET = """
NAME

    python-library set - Set specific versions of DAS Python libraries.

SYNOPSIS

    das-cli python-library set [--hyperon-das=<version>] [--hyperon-das-atomdb=<version>]

DESCRIPTION

    'das-cli python-library set' sets the versions of DAS Python libraries, such as hyperon-das and hyperon-das-atomdb, to the specified versions.
    This command requires at least one of the following parameters: --hyperon-das or --hyperon-das-atomdb.

OPTIONS

--hyperon-das=<version>

    Set the version of the hyperon-das library to the specified version.
    Available versions can be found at https://github.com/singnet/das-query-engine/releases.

--hyperon-das-atomdb=<version>

    Set the version of the hyperon-das-atomdb library to the specified version.
    Available versions can be found at https://github.com/singnet/das-atom-db/releases.


EXAMPLES

    Set the version of the hyperon-das library to version 1.2.0.

    $ das-cli python-library set --hyperon-das=1.2.0

    Set the version of the hyperon-das-atomdb library to version 0.4.0.

    $ das-cli python-library set --hyperon-das-atomdb=0.4.0
"""

SHORT_HELP_LIB_SET = "Allow setting specific versions for both hyperon-das and hyperon-das-atomdb libraries"

HELP_LIB_UPD = "Update both hyperon-das and hyperon-das-atomdb to the newest available or to a specific version."

SHORT_HELP_LIB_UPD = """
NAME

    python-library update - Update DAS Python libraries to the latest available versions.

SYNOPSIS

    das-cli python-library update

DESCRIPTION

    'das-cli python-library update' updates the versions of DAS Python libraries, such as hyperon-das and hyperon-das-atomdb, to the latest available versions.

EXAMPLES

    Update all Python libraries to their latest versions.

    $ das-cli python-library update
"""

HELP_PYLIB = """
NAME

    python-library - Manage versions of DAS Python libraries.

SYNOPSIS

    das-cli python-library <command> [options]

DESCRIPTION

    'das-cli python-library' allows you to manage versions of DAS Python libraries, such as hyperon-das and hyperon-das-atomdb.
    This tool provides commands to list available versions, set specific versions, update to the latest versions, and display installed versions of Python libraries.

COMMANDS

    list            List available versions of DAS Python libraries.
    set             Set specific versions of DAS Python libraries.
    update          Update DAS Python libraries to the latest versions.
    version         Show installed and latest versions of DAS Python libraries.

EXAMPLES

    List available versions:

        $ das-cli python-library list

    Set specific versions:

        $ das-cli python-library set --hyperon-das=1.2.0

    Update all libraries to latest:

        $ das-cli python-library update

    Show installed versions:

        $ das-cli python-library version
"""

SHORT_HELP_PYLIB = "Manage versions of Python libraries."
