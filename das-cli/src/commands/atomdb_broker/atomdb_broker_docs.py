SHORT_HELP_START = "Starts the AtomDb Broker agent"

HELP_START = '''
NAME

    das-cli atomdb-broker start - Start the atomdb-broker service

SYNOPSIS

    das-cli atomdb-broker start [--port-range <start:end>]

DESCRIPTION

    Starts the AtomDb Broker service in a Docker container. If the service is already running,
    a warning will be shown.

    The service begins listening on the configured port.

EXAMPLES

    Start the AtomDb Broker service:

        $ das-cli atomdb-broker start --port-range 47000:47999
'''
HELP_STOP = '''
NAME

    das-cli atomdb-broker stop - Stop the AtomDB Broker service

SYNOPSIS

    das-cli atomdb-broker stop

DESCRIPTION

    Stops the currently running AtomDB Broker container. This halts the processing of messages
    and deactivates the service until it is explicitly started again.

    If the service is already stopped, a warning message is displayed.

EXAMPLES

    Stops the AtomDb Broker service:

        $ das-cli atomdb-broker stop
'''

SHORT_HELP_STOP = "Starts the AtomDb Broker agent"

HELP_RESTART = """
NAME

    das-cli atomdb-broker restart - Restart the AtomDB Broker service

SYNOPSIS

    das-cli atomdb-broker restart

DESCRIPTION

    This command combines a stop and a start operation to ensure that the
    AtomDB Broker is restarted cleanly.

    Useful for refreshing configurations or recovering from faults.

EXAMPLES

    Restart the AtomDB Broker service:

        $ das-cli atomdb-broker restart
"""

SHORT_HELP_RESTART = "Restart the AtomDB Broker service."

HELP_ATOMDB_BROKER = """
NAME

    das-cli atomdb-broker - Manage the AtomDB Broker service

SYNOPSIS

    das-cli atomdb-broker [COMMAND]

DESCRIPTION

    This command group allows you to manage the lifecycle of the AtomDB Broker service,

COMMANDS
    start
        Start the AtomDB Broker service and begin message processing.

    stop
        Stop the currently running AtomDB Broker container.

    restart
        Restart the AtomDB Broker container (stop followed by start).

EXAMPLES
    Start the broker:

        $ das-cli atomdb-broker start

    Stop the broker:

        $ das-cli atomdb-broker stop

    Restart the broker:

        $ das-cli atomdb-broker restart
"""

SHORT_HELP_ATOMDB_BROKER = "Control the lifecycle of the AtomDB Broker service."
