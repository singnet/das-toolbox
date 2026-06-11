HELP_DATABASE_ADAPTER = """
NAME

    das-cli database-adapter - Group commands for managing the DAS peer server and DBMS peer client.

SYNOPSIS

    das-cli database-adapter <command> [OPTIONS]

DESCRIPTION

    The 'database-adapter' is a tool responsible for synchronizing SQL and NOSQL databases with the atomspace, the information inside the databases will
    effectively be mapped and turned into Atoms.

    The group contains the following subcommands:

COMMANDS

    database-adapter run ->

EXAMPLES

    View available commands in the database-adapter group:
        das-cli database-adapter run -> Runs the database adapter to synchronize a SQL/NoSQL database with the Atomspace.

"""

SHORT_HELP_DATABASE_ADAPTER = "Groups DBMS and DAS peer server commands for easier management."

HELP_RUN = "The 'run' method calls the database_adapter and starts mapping a database into Atoms."
SHORT_HELP_RUN = "Calls database-adapter to start mapping."

HELP_STOP = "The 'stop' command will abort and stop the container running the database-adapter"
SHORT_HELP_STOP = "Aborts the current running database-adapter instance."
