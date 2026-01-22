
HELP_START = """
NAME

    start - Start the Query Agent service

SYNOPSIS

    das-cli query-agent start [--port-range <start:end>]

DESCRIPTION

    Initializes and runs the Query Agent service.

EXAMPLES

    To start the Query Agent service:

        $ das-cli query-agent start --port-range 42000:42999
"""

SHORT_HELP_START = "Start the Query Agent service."

HELP_STOP = """
NAME

    stop - Stop the Query Agent service

SYNOPSIS

    das-cli query-agent stop

DESCRIPTION

    Stops the running Query Agent service.

EXAMPLES

    To stop a running Query Agent service:

    $ das-cli query-agent stop
"""

SHORT_HELP_STOP = "Stop the Query Agent service."

HELP_RESTART = """
NAME

    restart - Restart the Query Agent service

SYNOPSIS

    das-cli query-agent restart [--port-range <start:end>]

DESCRIPTION

    Stops and then starts the Query Agent service.

    This command ensures a frinstance of the Query Agent is running.

EXAMPLES

    To restart the Query Agent service:

        $ das-cli query-agent restart --port-range 42000:42999

"""

SHORT_HELP_RESTART = "Restart the Query Agent service."

HELP_QA = """
NAME

    query-agent - Manage the Query Agent service

SYNOPSIS

    das-cli query-agent <command> [options]

DESCRIPTION

    Provides commands to control the Query Agent service.

    Use this command group to start, stop, or restart the service.

COMMANDS

    start

        Start the Query Agent service.

    stop

        Stop the Query Agent service.

    restart

        Restart the Query Agent service.

EXAMPLES

    Start the Query Agent service:

        $ das-cli query-agent start --port-range 42000:42999

    Stop the Query Agent service:

        $ das-cli query-agent stop

    Restart the Query Agent service:

        $ das-cli query-agent restart --port-range 42000:42999
"""

SHORT_HELP_QA = "Manage the Query Agent service."