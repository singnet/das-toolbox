HELP_LOAD = """
NAME

    das-cli metta load - Load a MeTTa file or directory of files into the database.

SYNOPSIS

    das-cli metta load <path>

DESCRIPTION

    Loads MeTTa files into the configured database using DAS CLI.

    The <path> argument must be an absolute path to a single `.metta` file or a directory
    containing `.metta` files. If a directory is given, all `.metta` files in the directory
    will be loaded. Only files with the `.metta` extension are considered.

    This operation requires that the MongoDB and Redis services are running.
    Use 'das-cli db start' to start the necessary containers before loading.

ARGUMENTS

    <path>

        Absolute path to a .metta file or directory containing .metta files.
        Relative paths are not supported.

EXAMPLES

    Load a single MeTTa file into the database:

        $ das-cli metta load /absolute/path/to/animals.metta

    Load all MeTTa files in a directory:

        $ das-cli metta load /absolute/path/to/mettas-directory
"""

SHORT_HELP_LOAD = "Load a MeTTa file into the databases."

HELP_CHECK = """
NAME

    das-cli metta check - Validate the syntax of MeTTa files without loading them.

SYNOPSIS

    das-cli metta check <path>

DESCRIPTION

    Validates the syntax of a .metta file or all .metta files in a directory.

    This command checks that each MeTTa file is syntactically correct without
    inserting any data into the database. It is useful to catch errors before
    attempting a full load using 'das-cli metta load'.

ARGUMENTS

    <path>

        Absolute path to a .metta file or a directory containing .metta files.
        Relative paths are not supported.

EXAMPLES

    Validate the syntax of a single MeTTa file:

        $ das-cli metta check /absolute/path/to/animals.metta

    Validate the syntax of all files in a directory:

        $ das-cli metta check /absolute/path/to/mettas-directory
"""

SHORT_HELP_CHECK = "Validate syntax of MeTTa files used with the DAS CLI"

HELP_METTA = """
NAME
    das-cli metta - Manage operations related to MeTTa files.

SYNOPSIS
    das-cli metta <subcommand> [OPTIONS]

DESCRIPTION
    Provides a command group for managing MeTTa knowledge base files. This group
    includes commands for syntax validation and database loading.

    Available subcommands:

        load    Load MeTTa files into the database
        check   Validate syntax of MeTTa files

    Use `das-cli metta check` to quickly check for syntax errors before running
    `das-cli metta load`, which performs the actual data loading.

EXAMPLES
    Check MeTTa syntax before loading:

        $ das-cli metta check /absolute/path/to/mettas-directory

    Load MeTTa files into the database:

        $ das-cli metta load /absolute/path/to/mettas-directory
"""

SHORT_HELP_METTA = "Manage operations related to the loading of MeTTa files."
