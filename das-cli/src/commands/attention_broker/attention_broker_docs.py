# ==== Stop commands ==== #

HELP_STOP = """
NAME

    das-cli attention-broker stop - Stop the running Attention Broker service

SYNOPSIS

    das-cli attention-broker stop

DESCRIPTION

    Stops the currently running Attention Broker container. This halts the processing of messages
    and deactivates the broker until it is explicitly started again.

    If the service is already stopped, a warning message is displayed.

EXAMPLES

    Stop the running Attention Broker service:

        $ das-cli attention-broker stop
"""

SHORT_HELP_STOP = "Stop the running Attention Broker service"

# ==== Start commands ==== #

HELP_START = """
NAME

    das-cli attention-broker start - Start the Attention Broker service

SYNOPSIS

    das-cli attention-broker start

DESCRIPTION

    Starts the Attention Broker service in a Docker container. If the service is already running,
    a warning will be shown.

    The broker begins listening on the configured port and processes messages accordingly.

EXAMPLES

    Start the Attention Broker service:

        $ das-cli attention-broker start
"""

SHORT_HELP_START = "Start the Attention Broker service."

HELP_RESTART = """
NAME

    das-cli attention-broker restart - Restart the Attention Broker service

SYNOPSIS

    das-cli attention-broker restart

DESCRIPTION

    This command combines a stop and a start operation to ensure that the
    Attention Broker is restarted cleanly.

    Useful for refreshing configurations or recovering from faults.

EXAMPLES

    Restart the Attention Broker service:

        $ das-cli attention-broker restart
"""

SHORT_HELP_RESTART = "Restart the Attention Broker service."

HELP_ATTENTION_BROKER = """
NAME

    das-cli attention-broker - Manage the Attention Broker service

SYNOPSIS

    das-cli attention-broker [COMMAND]

DESCRIPTION

    This command group allows you to manage the lifecycle of the Attention Broker service,
    which is responsible for  tracks atom importance values in different contexts and updates those values based on user queries using context-specific Hebbian networks.

COMMANDS
    start
        Start the Attention Broker service and begin message processing.

    stop
        Stop the currently running Attention Broker container.

    restart
        Restart the Attention Broker container (stop followed by start).

EXAMPLES
    Start the broker:

        $ das-cli attention-broker start

    Stop the broker:

        $ das-cli attention-broker stop

    Restart the broker:

        $ das-cli attention-broker restart
"""

SHORT_HELP_ATTENTION_BROKER = "Control the lifecycle of the Attention Broker service."