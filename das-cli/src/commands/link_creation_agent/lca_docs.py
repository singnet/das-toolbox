HELP_STOP = """
NAME

    link-creation-agent stop - Stop the Link Creation Agent service

SYNOPSIS

    das-cli link-creation-agent stop

DESCRIPTION

    Stops the running Link Creation Agent service container.

EXAMPLES

    To stop a running Link Creation Agent service:

        das-cli link-creation-agent stop
"""

SHORT_HELP_STOP = "Stop the Link Creation Agent service."

HELP_START = """
NAME

    link-creation-agent start - Start the Link Creation Agent service

SYNOPSIS

    das-cli link-creation-agent start [--port-range <start_port-end_port>]

DESCRIPTION

    Initializes and runs the Link Creation Agent service.
    Connects to the query engine using agents.query.endpoint from the config file.

EXAMPLES

    To start the Link Creation Agent service:

        das-cli link-creation-agent start --port-range 43000:43999
"""

SHORT_HELP_START = "Start the Link Creation Agent service."

HELP_RESTART = """
NAME

    link-creation-agent restart - Restart the Link Creation Agent service

SYNOPSIS

    das-cli link-creation-agent restart [--port-range <start_port-end_port>]

DESCRIPTION

    Stops and then starts the Link Creation Agent service.

EXAMPLES

    To restart the Link Creation Agent service:

        das-cli link-creation-agent restart --port-range 43000:43999
"""

SHORT_HELP_RESTART = "Restart the Link Creation Agent service."

HELP_LCA = """
NAME

    link-creation-agent - Manage the Link Creation Agent service

SYNOPSIS

    das-cli link-creation-agent <command> [options]

DESCRIPTION

    Provides commands to control the Link Creation Agent service lifecycle.

COMMANDS

    start       Start the Link Creation Agent service.
    stop        Stop the Link Creation Agent service.
    restart     Restart the Link Creation Agent service.

EXAMPLES

    Start the service:

        das-cli link-creation-agent start --port-range 43000:43999

    Stop the service:

        das-cli link-creation-agent stop

    Restart the service:

        das-cli link-creation-agent restart --port-range 43000:43999
"""

SHORT_HELP_LCA = "Manage the Link Creation Agent service."
