HELP_START = """
NAME

    vault start - Start the Vault (OpenBao) service

SYNOPSIS

    das-cli vault start

DESCRIPTION

    Starts an OpenBao server in a Docker container with the web UI enabled.
    The listen address is read from vault.endpoint in the JSON
    configuration file.

    A strong admin password is generated and printed once. Use it to log in
    at http://<host>:<port>/ui and complete the dashboard setup.

EXAMPLES

    Start Vault:

        $ das-cli vault start
"""

SHORT_HELP_START = "Start the Vault (OpenBao) service."

HELP_STOP = """
NAME

    vault stop - Stop the running Vault (OpenBao) service

SYNOPSIS

    das-cli vault stop

DESCRIPTION

    Stops and removes the Vault container.

    If the service is already stopped, a warning message is displayed.

EXAMPLES

    Stop Vault:

        $ das-cli vault stop
"""

SHORT_HELP_STOP = "Stop the running Vault (OpenBao) service."

HELP_VAULT = """
NAME

    vault - Manage the Vault (OpenBao) service

SYNOPSIS

    das-cli vault [COMMAND]

DESCRIPTION

    Starts and stops a local OpenBao instance used as the DAS vault. 
    The UI is enabled so you can configure the vault from the browser.

COMMANDS

    start       Start the Vault service and print the admin password.
    stop        Stop the running Vault container.

EXAMPLES

    Start Vault:

        $ das-cli vault start

    Stop Vault:

        $ das-cli vault stop
"""

SHORT_HELP_VAULT = "Manage the Vault (OpenBao) service."
