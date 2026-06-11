SHORT_HELP_START = "Starts the Command Router service"

HELP_START = '''
NAME

    das-cli command-router start - Start the command router service

SYNOPSIS

    das-cli command-router start [--port-range <start:end>]

DESCRIPTION

    Starts the command router service in a Docker container. If the service is already running,
    a warning will be shown.

    The service begins listening on the configured port.

EXAMPLES

    Start the command router service:

        $ das-cli command-router start --port-range 47000:47999
'''
HELP_STOP = '''
NAME

    das-cli command-router stop - Stop the Command Router service

SYNOPSIS

    das-cli command-router stop

DESCRIPTION

    Stops the currently running Command Router container. This halts the processing of messages
    and deactivates the service until it is explicitly started again.

    If the service is already stopped, a warning message is displayed.

EXAMPLES

    Stops the command router service:

        $ das-cli command-router stop
'''

SHORT_HELP_STOP = "Starts the command router agent"

HELP_RESTART = """
NAME

    das-cli command-router restart - Restart the Command Router service

SYNOPSIS

    das-cli command-router restart

DESCRIPTION

    This command combines a stop and a start operation to ensure that the
    Command Router is restarted cleanly.

    Useful for refreshing configurations or recovering from faults.

EXAMPLES

    Restart the Command Router service:

        $ das-cli command-router restart
"""

SHORT_HELP_RESTART = "Restart the Command Router service."

HELP_COMMAND_ROUTER = """
NAME

    das-cli command-router - Manage the Command Router service

SYNOPSIS

    das-cli command-router [COMMAND]

DESCRIPTION

    This command group allows you to manage the lifecycle of the Command Router service,

COMMANDS
    start
        Start the Command Router service and begin message processing.

    stop
        Stop the currently running Command Router container.

    restart
        Restart the Command Router container (stop followed by start).

EXAMPLES
    Start the broker:

        $ das-cli command-router start

    Stop the broker:

        $ das-cli command-router stop

    Restart the broker:

        $ das-cli command-router restart
"""

SHORT_HELP_COMMAND_ROUTER = "Control the lifecycle of the Command Router service."
