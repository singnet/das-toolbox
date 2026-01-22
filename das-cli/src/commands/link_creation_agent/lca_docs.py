HELP_STOP = """
NAME

    link-creation-agent stop - Stop the Link Creation Agent service

SYNOPSIS

    das-cli link-creation-agent stop

DESCRIPTION

    Stops the running Link Creation Agent service container.
    If the service is already stopped, a warning is shown.

EXAMPLES

    To stop a running Link Creation Agent service:

        das-cli link-creation-agent stop
"""

SHORT_HELP_STOP = "Stop the Link Creation Agent service."

HELP_START = """
NAME

    link-creation-agent start - Start the Link Creation Agent service

SYNOPSIS

    das-cli link-creation-agent start [--peer-hostname <hostname>] [--peer-port <port>]
    [--port-range <start_port-end_port>]

DESCRIPTION

    Initializes and runs the Link Creation Agent service.
    This command starts the service container and reports the ports where it is listening.
    Ensure the required dependent services (like Query Agent) are running before starting.

EXAMPLES

    To start the Link Creation Agent service:

        das-cli link-creation-agent start --peer-hostname localhost --peer-port 40002 --port-range 43000:43999
"""

SHORT_HELP_START = "Start the Link Creation Agent service."

HELP_RESTART = "Restart the Link Creation Agent service."

SHORT_HELP_RESTART = """
NAME

    link-creation-agent restart - Restart the Link Creation Agent service

SYNOPSIS

    das-cli link-creation-agent restart [--peer-hostname <hostname>] [--peer-port <port>]
    [--port-range <start_port-end_port>]

DESCRIPTION

    Stops the currently running Link Creation Agent service and then starts a fresh instance.
    Useful for refreshing the service or applying configuration changes.

EXAMPLES

    To restart the Link Creation Agent service:

        das-cli link-creation-agent restart --peer-hostname localhost --peer-port 40002 --port-range 43000:43999
"""

HELP_LCA = """
NAME

    link-creation-agent - Manage the Link Creation Agent service

SYNOPSIS

    das-cli link-creation-agent <command> [options]

DESCRIPTION

    Provides commands to control the Link Creation Agent service lifecycle.
    Use this command group to start, stop, or restart the service.

COMMANDS

    start       Start the Link Creation Agent service.
    stop        Stop the Link Creation Agent service.
    restart     Restart the Link Creation Agent service.

EXAMPLES

    Start the service:

        das-cli link-creation-agent start --peer-hostname localhost --peer-port 40002 --port-range 43000:43999

    Stop the service:

        das-cli link-creation-agent stop

    Restart the service:

        das-cli link-creation-agent restart --peer-hostname localhost --peer-port 40002 --port-range 43000:43999
"""

SHORT_HELP_LCA = "Manage the Link Creation Agent service."