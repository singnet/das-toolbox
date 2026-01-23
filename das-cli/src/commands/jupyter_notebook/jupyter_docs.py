HELP_START = """
NAME

    jupyter-notebook start - Start a Jupyter Notebook environment

SYNOPSIS

    das-cli jupyter-notebook start [--working-dir <directory>]

DESCRIPTION

    Starts a Jupyter Notebook environment by launching a Jupyter server locally.
    This allows you to create, edit, and run Python notebooks interactively via your web browser.
    After starting, the command displays the port number where the server is listening.
    Access the notebook by navigating to 'localhost:<port>' in your browser.
    No token or password is required to access the notebook.

OPTIONS

    --working-dir, -w
        Optional. Specify a custom working directory to bind to the Jupyter Notebook container.

EXAMPLES

    Start a Jupyter Notebook environment:

        das-cli jupyter-notebook start

    Start a Jupyter Notebook with a custom working directory:

        das-cli jupyter-notebook start --working-dir /path/to/working/directory
"""

SHORT_HELP_START = "Start a Jupyter Notebook."

HELP_STOP = """
NAME

    jupyter-notebook stop - Stop a running Jupyter Notebook environment

SYNOPSIS

    das-cli jupyter-notebook stop

DESCRIPTION

    Stops the currently running Jupyter Notebook environment.

EXAMPLES

    Stop a running Jupyter Notebook environment:

        das-cli jupyter-notebook stop
"""

SHORT_HELP_STOP = "Stop a Jupyter Notebook."

HELP_RESTART = """
NAME

    jupyter-notebook restart - Restart a Jupyter Notebook environment

SYNOPSIS

    das-cli jupyter-notebook restart [--working-dir <directory>]

DESCRIPTION

    Restarts the Jupyter Notebook environment by stopping the current instance and starting a new one.
    Useful to refresh the environment or apply configuration changes.

OPTIONS

    --working-dir, -w
        Optional. Specify a custom working directory to bind to the Jupyter Notebook container.

EXAMPLES

    Restart the Jupyter Notebook environment:

        das-cli jupyter-notebook restart

    Restart with a custom working directory:

        das-cli jupyter-notebook restart --working-dir /path/to/working/directory
"""

SHORT_HELP_RESTART = "Restart Jupyter Notebook."

HELP_JUPYTER = """
NAME

    jupyter-notebook - Manage Jupyter Notebook environments

SYNOPSIS

    das-cli jupyter-notebook <command> [options]

DESCRIPTION

    Provides commands to start, stop, and restart Jupyter Notebook environments.
    Enables interactive creation, editing, and execution of Python notebooks.

COMMANDS

    start       Start a Jupyter Notebook environment.
    stop        Stop a running Jupyter Notebook environment.
    restart     Restart the Jupyter Notebook environment.

EXAMPLES

    Start the notebook:

        das-cli jupyter-notebook start

    Stop the notebook:

        das-cli jupyter-notebook stop

    Restart the notebook:

        das-cli jupyter-notebook restart
"""

SHORT_HELP_JUPYTER = "Manage Jupyter Notebook."
