# db_docs.py


HELP_DB_COUNT_ATOMS = """
.SH NAME

count-atoms - Displays counts of MongoDB atoms and Redis key patterns.

.SH DESCRIPTION

'das-cli db count-atoms' counts the atoms stored in MongoDB and shows counts of specific key patterns stored in Redis.
This is useful for monitoring and understanding the distribution and number of records in your databases.

.SH EXAMPLES

Run the command see the count of MongoDB atoms and the breakdown of Redis key patterns:

$ das-cli db count-atoms
"""

SHORT_HELP_DB_COUNT_ATOMS = "Displays counts of MongoDB atoms and Redis key patterns."


HELP_DB_STOP = """
.SH NAME

stop - Stops all DBMS containers.

.SH DESCRIPTION

'das-cli db stop' stops the DBMS containers that were previously started with 'das-cli db start'.
This command is useful for shutting down the databases when they are no longer needed.

IMPORTANT NOTE: After stopping the databases, all data will be lost.

.SH EXAMPLES

Stop DBMS containers previously started with 'das-cli db start'.

$ das-cli db stop

Stop DBMS containers and remove volumes.

$ das-cli db stop --prune
"""

SHORT_HELP_DB_STOP = "Stops all DBMS containers."


HELP_DB_START = """
.SH NAME

start - Starts all DBMS containers.

.SH DESCRIPTION

'das-cli db start' initiates all databases.

Upon execution, the command will display the ports on which each database is running.
Note that the port configuration can be modified using the 'das-cli config set' command.

.SH EXAMPLES

Start all databases for use with the DAS.

$ das-cli db start
"""

SHORT_HELP_DB_START = "Starts all DBMS containers."


HELP_DB_RESTART = """
.SH NAME

restart - Restart all DBMS containers.

.SH DESCRIPTION

'das-cli db restart' restarts all database containers previously started with 'das-cli db start'.
If no databases have been started, 'das-cli db restart' will simply start them.

IMPORTANT NOTE: Restarting the databases will result in all data being lost. Databases are started empty.

.SH EXAMPLES

Restart DBMS containers previously started with 'das-cli db start'.

$ das-cli db restart

Restart DBMS containers and remove their volumes.

$ das-cli db restart --prune
"""

SHORT_HELP_DB_RESTART = "Restart all DBMS containers."


HELP_DB_CLI = """
NAME

    das-cli db - Manage database-related operations for DAS.

SYNOPSIS

    das-cli db <command> [options]

DESCRIPTION

    Manage DAS backend DBMS required for for use with the DAS CLI.

    This command group allows you to control the lifecycle of local databases used by
    DAS components. It provides utilities to start, stop, and restart supported DBMSs.

COMMANDS

    start               Start the DAS database containers.
    stop                Stop the DAS database containers.
    restart             Restart the DAS database containers.
    count-atoms         Count the number of atoms currently stored in the database

EXAMPLES

    das-cli db start

        Start all DAS-related databases locally.

    das-cli db stop

        Stop all running DAS-related database containers.

    das-cli db restart

        Restart the DAS database services.

    das-cli db count-atoms

        Return the number of atoms currently stored in the database.
"""

SHORT_HELP_DB_CLI = "Manage db-related operations."
