HELP_STOP = """
NAME

    das-cli evolution-agent stop - Stop the running Evolution Agent service

SYNOPSIS

    das-cli evolution-agent stop

DESCRIPTION

    Stops the currently running Evolution Agent container. This halts the processing of messages
    and deactivates the agent until it is explicitly started again.

    If the service is already stopped, a warning message is displayed.

EXAMPLES

    Stop the running Evolution Agent service:

        $ das-cli evolution-agent stop
"""

SHORT_HELP_STOP = "Stop the running Evolution Agent service"

HELP_START = """
NAME

    das-cli evolution-agent start - Start the Evolution Agent service

SYNOPSIS

    das-cli evolution-agent start [--port-range <start:end>] [--peer-hostname <hostname>] [--peer-port <port>]

DESCRIPTION

    Starts the Evolution Agent service in a Docker container. If the service is already running,
    a warning will be shown.

    The agent begins listening on the configured port and processes messages accordingly.

EXAMPLES

    Start the Evolution Agent service:

        $ das-cli evolution-agent start --port-range 45000:45999 --peer-hostname localhost --peer-port 40002
"""

SHORT_HELP_START = "Start the Evolution Agent service."

HELP_RESTART = """
NAME

    das-cli evolution-agent restart - Restart the Evolution Agent service

SYNOPSIS

    das-cli evolution-agent restart [--peer-hostname <hostname>] [--peer-port <port>]  [--port-range <start:end>]

DESCRIPTION

    This command combines a stop and a start operation to ensure that the
    Evolution Agent is restarted cleanly.

    Useful for refreshing configurations or recovering from faults.

EXAMPLES

    Restart the Evolution Agent service:

        $ das-cli evolution-agent restart --port-range 45000:45999 --peer-hostname localhost --peer-port 40002
"""

SHORT_HELP_RESTART = "Restart the Evolution Agent service."

HELP_EVOLUTION_AGENT = """
NAME

    das-cli evolution-agent - Manage the Evolution Agent service

SYNOPSIS

    das-cli evolution-agent [COMMAND]

DESCRIPTION

    This command group allows you to manage the lifecycle of the Evolution Agent service,
    which is responsible for  tracks atom importance values in different contexts and updates those values based on user queries using context-specific Hebbian networks.

COMMANDS
    start
        Start the Evolution Agent service and begin message processing.

    stop
        Stop the currently running Evolution Agent container.

    restart
        Restart the Evolution Agent container (stop followed by start).

EXAMPLES
    Start the agent:

        $ das-cli evolution-agent start [--port-range <start:end>] [--peer-hostname <hostname>] [--peer-port <port>]

    Stop the agent:

        $ das-cli evolution-agent stop

    Restart the agent:

        $ das-cli evolution-agent restart [--port-range <start:end>] [--peer-hostname <hostname>] [--peer-port <port>]
"""

SHORT_HELP_EVOLUTION_AGENT = "Control the lifecycle of the Evolution Agent service."