HELP_CONFIG_SET = """
NAME
    das-cli config set - Select active config path or update active config keys.

SYNOPSIS
    das-cli config set
    das-cli config set key=value


DESCRIPTION
     The 'config set' command supports two modes:

     1) No arguments:
         Shows an interactive prompt with two options:
         - Use default config
         - Create new custom config (saved to ~/.das/<name>.json)

         If "Use default config" is selected, the command activates the
         resolved default config path and removes only the saved configpath
         override from ~/.das/.env.

         If "Create new custom config" is selected, the command creates
         ~/.das/<name>.json (when missing) and activates it.

     2) key=value:
         Updates a single key in the active config file.

     Note: key=value updates are blocked when the active config is a
     system or packaged default configuration file.

     Note: interactive modes that depend on default config contents may fail
     if no default config file is available in the current installation.

SECTIONS

    - Interactive mode selection
    - Legacy key=value update mode


OPTIONS AND VARIABLES

SCHEMA VERSION (schema_version)

    Defines the version of the configuration schema used by DAS CLI.
    This is used internally to validate compatibility between CLI versions
    and configuration structure.


ATOMDB BACKEND (atomdb)

    atomdb.type
        Defines the backend used for AtomDB storage.
        Supported values:
        - redismongodb
        - morkdb
        - inmemorydb
        - remotedb


    REDIS CONFIGURATION (atomdb.redis)

        atomdb.redis.endpoint
            Redis connection endpoint in the format:
                host:port

        atomdb.redis.cluster
            Enable or disable Redis cluster mode (true/false).

        atomdb.redis.nodes
            List of Redis nodes used in cluster mode.

        atomdb.redis.nodes.[].context
            Docker context used to connect to the node.

        atomdb.redis.nodes.[].ip
            Node IP address.

        atomdb.redis.nodes.[].username
            SSH username used to access the node.


    MONGODB CONFIGURATION (atomdb.mongodb)

        atomdb.mongodb.endpoint
            MongoDB connection endpoint:
                host:port

        atomdb.mongodb.username
            Username used for authentication.

        atomdb.mongodb.password
            Password used for authentication.

        atomdb.mongodb.cluster
            Enable or disable MongoDB cluster mode (true/false).

        atomdb.mongodb.cluster_secret_key
            Shared key used between cluster nodes.

        atomdb.mongodb.nodes
            List of MongoDB nodes.

        atomdb.mongodb.nodes.[].context
            Docker context for remote execution.

        atomdb.mongodb.nodes.[].ip
            Node IP address.

        atomdb.mongodb.nodes.[].username
            SSH username for the node.


LOADERS (loaders)

    loaders.metta.image
        Docker image used for the MeTTa loader.

    loaders.morkdb.image
        Docker image used for the MorkDB loader.


VAULT (vault)

    vault.endpoint
        Local loopback endpoint where the Vault (OpenBao) server is published
        on the host, in the form host:port. Hostname must be localhost or
        127.0.0.1. Inside the container, OpenBao listens on 0.0.0.0.


AGENTS (agents)

    agents.query.endpoint
        Endpoint for the Query Agent.

    agents.query.ports_range
        Range of ports used by Query Agent workers.

    agents.link_creation.endpoint
        Endpoint for the Link Creation Agent.

    agents.link_creation.ports_range
        Range of ports used by Link Creation workers.

    agents.evolution.endpoint
        Endpoint for the Evolution Agent.

    agents.evolution.ports_range
        Range of ports used by Evolution workers.


BROKERS (brokers)

    brokers.attention.endpoint
        Endpoint for the Attention Broker.

    brokers.context.endpoint
        Endpoint for the Context Broker.

    brokers.context.ports_range
        Port range for Context Broker workers.

    brokers.atomdb.endpoint
        Endpoint for the AtomDB Broker.

    brokers.atomdb.ports_range
        Port range for AtomDB Broker workers.


PARAMETERS (params)

    params.query.max_answers
    params.query.max_bundle_size
    params.query.count_flag
    params.query.attention_update_flag
    params.query.unique_assignment_flag
    params.query.positive_importance_flag
    params.query.populate_metta_mapping
    params.query.use_metta_as_query_tokens

        Runtime parameters controlling query execution behavior.


    params.link_creation.repeat_count
    params.link_creation.query_interval
    params.link_creation.query_timeout

        Controls link creation execution behavior.


    params.evolution.elitism_rate
    params.evolution.max_generations
    params.evolution.population_size
    params.evolution.selection_rate
    params.evolution.total_attention_tokens

        Controls evolutionary algorithm behavior.


    params.context.context
    params.context.use_cache
    params.context.enforce_cache_recreation
    params.context.initial_rent_rate
    params.context.initial_spreading_rate_lowerbound
    params.context.initial_spreading_rate_upperbound

        Controls context management behavior.


ENVIRONMENT (environment)

    environment.jupyter.endpoint
        Endpoint where Jupyter Notebook server is exposed.


EXAMPLES

    Select active config interactively:

        $ das-cli config set

    Select default config (press Enter to keep the default option):

        $ printf "\n" | das-cli config set

    Set a configuration option on the active custom config:

        $ das-cli config set atomdb.mongodb.endpoint="localhost:40040"

    Create and activate a custom config interactively:

        $ das-cli config set
        # choose: Create new custom config
        # enter file name: my-config

"""

SHORT_HELP_CONFIG_SET = "Activate default config or create ~/.das/<name>.json; set key=value on active custom config."

HELP_CONFIG_LIST = """Display all current configuration values used by the DAS CLI.

NAME

    das-cli config list - Display current configuration settings

SYNOPSIS

    das-cli config list [key]

DESCRIPTION

    The 'das-cli config list' command prints all the current configuration settings
    that have been applied to the DAS CLI. The output is presented in a structured
    table format, which includes settings for various DAS components such as Redis,
    MongoDB, OpenFaaS, and others.

EXAMPLES

    To display the current configuration values, run:

        $ das-cli config list

    To display the value of a specific configuration key, run:

        $ das-cli config list services.query_agent.port

"""

SHORT_HELP_CONFIG_LIST = "Display all current configuration values used by the DAS CLI."

HELP_CONFIG = """
NAME

    das-cli config - Manage configuration settings

SYNOPSIS

    das-cli config [subcommand]

DESCRIPTION

    The 'das-cli config' command group provides a unified interface for managing
    the configuration settings of the DAS CLI. The configuration parameters include
    settings such as port numbers, usernames, container names, and clustering options
    for various services such as Redis, MongoDB, OpenFaaS, Jupyter Notebook, and more.

SUBCOMMANDS

    set
        Interactively set or update configuration parameters.
        See "das-cli config set" for more details.

    list
        Display the current configuration settings.
        See "das-cli config list" for more details.

USAGE

    To set the configuration values interactively:

        $ das-cli config set

    To list the current configuration settings:

        $ das-cli config list [key]
    """

SHORT_HELP_CONFIG = "Manage configuration settings for services used by the DAS CLI."
