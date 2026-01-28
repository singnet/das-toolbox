HELP_STOP = """
NAME

    inference-agent stop - Stop the Inference Agent service

SYNOPSIS

    das-cli inference-agent stop

DESCRIPTION

    Stops the running Inference Agent service.
    If the service is not running, a warning is shown.

EXAMPLES

    To stop the Inference Agent service:

        das-cli inference-agent stop
"""

SHORT_HELP_STOP = "Stop the Inference Agent service."

HELP_START = """
NAME

    inference-agent start - Start the Inference Agent service

SYNOPSIS

    das-cli inference-agent start [--peer-hostname <hostname>] [--peer-port <port>] [--port-range <start:end>]

DESCRIPTION

    Starts the Inference Agent service, initializing the required containers and ports.
    Checks that dependent services (e.g., Attention Broker) are running before starting.
    Shows the ports on which the service is listening.

EXAMPLES

    To start the Inference Agent service:

        das-cli inference-agent start --peer-hostname localhost --peer-port 40002 --port-range 44000:44999
"""

SHORT_HELP_START = "Start the Inference Agent service."

HELP_RESTART = """
NAME

    inference-agent restart - Restart the Inference Agent service

SYNOPSIS

    das-cli inference-agent restart [--peer-hostname <hostname>] [--peer-port <port>] [--port-range <start:end>]

DESCRIPTION

    Stops the running Inference Agent service and then starts it again.
    Useful for applying changes or recovering the service state.

EXAMPLES

    To restart the Inference Agent service:

        das-cli inference-agent restart --peer-hostname localhost --peer-port 40002 --port-range 44000:44999
"""

SHORT_HELP_RESTART = "Restart the Inference Agent service."

HELP_INFERENCE = """
NAME

    inference-agent - Commands to manage the Inference Agent service

SYNOPSIS

    das-cli inference-agent <command>

DESCRIPTION

    Provides commands to start, stop, and restart the Inference Agent service.

COMMANDS

    start       Start the Inference Agent service.
    stop        Stop the Inference Agent service.
    restart     Restart the Inference Agent service.

EXAMPLES

    Start the service:

        das-cli inference-agent start

    Stop the service:

        das-cli inference-agent stop

    Restart the service:

        das-cli inference-agent restart
"""

SHORT_HELP_INFERENCE = "Manage the Inference Agent service."
