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

    das-cli context-broker start [--port-range <start:end>] [--peer-hostname <hostname>] [--peer-port <port>]

DESCRIPTION

    Initializes and runs the Context Broker service.

EXAMPLES

    To start the Context Broker service:

        $ das-cli context-broker start --port-range 46000:46999 --peer-hostname localhost --peer-port 42000
"""

SHORT_HELP_START = "Start the Context Broker service."

HELP_RESTART = """
NAME

    restart - Restart the Context Broker service

SYNOPSIS

    das-cli context-broker restart [--peer-hostname <hostname>] [--peer-port <port>]  [--port-range <start:end>]

DESCRIPTION

    Stops and then starts the Context Broker service.

    This command ensures a instance of the Context Broker is running.

EXAMPLES

    To restart the Context Broker service:

        $ das-cli context-broker restart --port-range 46000:46999 --peer-hostname localhost --peer-port 42000

"""

SHORT_HELP_RESTART = "Restart the Context Broker service."

HELP_CONTEXT_BROKER = """
NAME

    context-broker - Manage the Context Broker service

SYNOPSIS

    das-cli context-broker <command> [options]

DESCRIPTION

    Provides commands to control the Context Broker service.

    Use this command group to start, stop, or restart the service.

COMMANDS

    start

        Start the Context Broker service.

    stop

        Stop the Context Broker service.

    restart

        Restart the Context Broker service.

EXAMPLES

    Start the Context Broker service:

        $ das-cli context-broker start --port-range 46000:46999 --peer-hostname localhost --peer-port 42000

    Stop the Context Broker service:

        $ das-cli context-broker stop

    Restart the Context Broker service:

        $ das-cli context-broker restart --port-range 46000:46999 --peer-hostname localhost --peer-port 42000
"""

SHORT_HELP_CONTEXT_BROKER = "Manage the Context Broker service."
