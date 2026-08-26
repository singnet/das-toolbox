HELP_START = """
NAME

    vault start - Start the Vault (OpenBao) service

SYNOPSIS

    das-cli vault start

DESCRIPTION

    Starts an OpenBao server in production mode in a Docker container, with
    persistent storage and the web UI enabled. The host-published endpoint is
    read from vault.endpoint in the JSON configuration file and must be a
    loopback address (localhost or 127.0.0.1). Inside the container, OpenBao
    listens on 0.0.0.0 on the configured port.

    After the container is up, OpenBao is initialized automatically with 3
    unseal keys. Those keys and the root token are printed together so you
    can store them elsewhere. Vault is then unsealed with the generated keys.

    If the container later stops or crashes, start prompts you to enter the
    unseal keys. das-cli does not store them.

    TLS is disabled for local use. This is not a substitute for a hardened
    production deployment.

EXAMPLES

    Start Vault:

        $ das-cli vault start
"""

SHORT_HELP_START = "Start the Vault (OpenBao) service."

HELP_STOP = """
NAME

    vault stop - Stop the running Vault (OpenBao) service

SYNOPSIS

    das-cli vault stop [--prune|-p]

DESCRIPTION

    Stops and removes the Vault container. Stored Vault data is kept so the
    next start can unseal the existing instance.

    Use --prune (or -p) to also delete the Vault data volume. After that,
    the next start will initialize a new Vault.

    If the service is already stopped, a warning message is displayed. With
    --prune, the data volume is still removed.

EXAMPLES

    Stop Vault:

        $ das-cli vault stop

    Stop Vault and delete stored data:

        $ das-cli vault stop --prune
        $ das-cli vault stop -p
"""

SHORT_HELP_STOP = "Stop the running Vault (OpenBao) service."

HELP_VAULT = """
NAME

    vault - Manage the Vault (OpenBao) service

SYNOPSIS

    das-cli vault [COMMAND]

DESCRIPTION

    Starts and stops a local OpenBao instance used as the DAS vault.
    The server runs in production mode (initialized, sealed, persistent
    storage). The UI is enabled so you can configure the vault from the
    browser after unsealing.

COMMANDS

    start       Start the Vault service and run interactive setup.
    stop        Stop the running Vault container.

EXAMPLES

    Start Vault:

        $ das-cli vault start

    Stop Vault:

        $ das-cli vault stop
"""

SHORT_HELP_VAULT = "Manage the Vault (OpenBao) service."
