HELP_STOP = """
NAME

    stop - Stop the Context Broker service

SYNOPSIS

    das-cli context-broker stop

DESCRIPTION

    Stops the running Context Broker service.

EXAMPLES

    To stop a running Context Broker service:

    $ das-cli context-broker stop
"""

SHORT_HELP_STOP = "Stop the Context Broker service."

HELP_START = """
NAME

    start - Start the Context Broker service

SYNOPSIS

    das-cli context-broker start [--port-range <start:end>]

DESCRIPTION

    Initializes and runs the Context Broker service.
    Connects to the query engine using agents.query.endpoint from the config file.

EXAMPLES

    To start the Context Broker service:

        $ das-cli context-broker start --port-range 46000:46999
"""

SHORT_HELP_START = "Start the Context Broker service."

HELP_RESTART = """
NAME

    restart - Restart the Context Broker service

SYNOPSIS

    das-cli context-broker restart [--port-range <start:end>]

DESCRIPTION

    Stops and then starts the Context Broker service.

EXAMPLES

    To restart the Context Broker service:

        $ das-cli context-broker restart --port-range 46000:46999
"""

SHORT_HELP_RESTART = "Restart the Context Broker service."

HELP_CONTEXT_BROKER = """
NAME

    context-broker - Manage the Context Broker service

SYNOPSIS

    das-cli context-broker <command> [options]

DESCRIPTION

    Provides commands to control the Context Broker service.

COMMANDS

    start       Start the Context Broker service.
    stop        Stop the Context Broker service.
    restart     Restart the Context Broker service.

EXAMPLES

    Start the Context Broker service:

        $ das-cli context-broker start --port-range 46000:46999

    Stop the Context Broker service:

        $ das-cli context-broker stop

    Restart the Context Broker service:

        $ das-cli context-broker restart --port-range 46000:46999
"""

SHORT_HELP_CONTEXT_BROKER = "Manage the Context Broker service."
