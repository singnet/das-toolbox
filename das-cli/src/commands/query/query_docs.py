HELP_QUERY = """
NAME

    query - Execute queries via command-router

SYNOPSIS

    das-cli query <command> [options]

DESCRIPTION

    Provides commands to execute a query and stream answers in real time.

COMMANDS

    run

        Execute a query and stream answers in real time.

EXAMPLES

    Execute and stream query results:

    $ das-cli query run 'LINK_TEMPLATE Expression 3 NODE Symbol Similarity NODE Symbol "human" VARIABLE S'
"""

SHORT_HELP_QUERY = "Execute queries via command-router."

HELP_RUN = """
NAME

    run - Execute a query via command-router and stream answers in real time

SYNOPSIS

    das-cli query run <query-text>

DESCRIPTION

    Submits a query execution request to command-router and streams answers until
    terminal status is reached.

    Query execution parameters are loaded from the active configuration file
    using `agents.base_query.params` merged with `agents.query.params`.

    Use `das-cli config list` to inspect those values and `das-cli config set`
    to change them.
"""

SHORT_HELP_RUN = "Execute query and stream answers in real time."