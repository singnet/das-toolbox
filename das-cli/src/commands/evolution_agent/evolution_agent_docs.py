HELP_STOP = """
NAME

    das-cli evolution-agent stop - Stop the running Evolution Agent service

SYNOPSIS

    das-cli evolution-agent stop

DESCRIPTION

    Stops the currently running Evolution Agent container.

EXAMPLES

    Stop the running Evolution Agent service:

        $ das-cli evolution-agent stop
"""

SHORT_HELP_STOP = "Stop the running Evolution Agent service"

HELP_START = """
NAME

    das-cli evolution-agent start - Start the Evolution Agent service

SYNOPSIS

    das-cli evolution-agent start [--port-range <start:end>]

DESCRIPTION

    Starts the Evolution Agent service in a Docker container.
    Connects to the query engine using agents.query.endpoint from the config file.

EXAMPLES

    Start the Evolution Agent service:

        $ das-cli evolution-agent start --port-range 45000:45999
"""

SHORT_HELP_START = "Start the Evolution Agent service."

HELP_RESTART = """
NAME

    das-cli evolution-agent restart - Restart the Evolution Agent service

SYNOPSIS

    das-cli evolution-agent restart [--port-range <start:end>]

DESCRIPTION

    Stops and then starts the Evolution Agent service.

EXAMPLES

    Restart the Evolution Agent service:

        $ das-cli evolution-agent restart --port-range 45000:45999
"""

SHORT_HELP_RESTART = "Restart the Evolution Agent service."

HELP_EVOLUTION_AGENT = """
NAME

    das-cli evolution-agent - Manage the Evolution Agent service

SYNOPSIS

    das-cli evolution-agent [COMMAND]

DESCRIPTION

    Manage the lifecycle of the Evolution Agent service.

COMMANDS

    start       Start the Evolution Agent service.
    stop        Stop the Evolution Agent service.
    restart     Restart the Evolution Agent service.

EXAMPLES

    Start the agent:

        $ das-cli evolution-agent start --port-range 45000:45999

    Stop the agent:

        $ das-cli evolution-agent stop

    Restart the agent:

        $ das-cli evolution-agent restart --port-range 45000:45999
"""

SHORT_HELP_EVOLUTION_AGENT = "Control the lifecycle of the Evolution Agent service."
