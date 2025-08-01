import getpass

VERSION = '0.4.14'
RELEASE_NOTES_URL = "https://raw.githubusercontent.com/singnet/das/master/docs/release-notes.md"

# PATHS

USER_DAS_PATH = "~/.das"

SECRETS_PATH = f"{USER_DAS_PATH}/config.json"

# LOG

LOG_FILE_NAME = f"/tmp/{getpass.getuser()}-das-cli.log"

# SERVICES

REDIS_IMAGE_NAME = "redis"
REDIS_IMAGE_VERSION = "7.2.3-alpine"

MONGODB_IMAGE_NAME = "mongo"
MONGODB_IMAGE_VERSION = "6.0.13-jammy"

METTA_PARSER_IMAGE_NAME = "trueagi/das"
METTA_PARSER_IMAGE_VERSION = "0.5.7-metta-parser"

OPENFAAS_IMAGE_NAME = "trueagi/openfaas"

JUPYTER_NOTEBOOK_IMAGE_NAME = "trueagi/das"
JUPYTER_NOTEBOOK_IMAGE_VERSION = "latest-jupyter-notebook"

DAS_PEER_IMAGE_NAME = "trueagi/das"
DAS_PEER_IMAGE_VERSION = "latest-database-adapter-server"

DBMS_PEER_IMAGE_NAME = "trueagi/das"
DBMS_PEER_IMAGE_VERSION = "latest-database-adapter-client"

ATTENTION_BROKER_IMAGE_NAME = "trueagi/das"
ATTENTION_BROKER_IMAGE_VERSION = "attention-broker-0.10.3"

QUERY_AGENT_IMAGE_NAME = "trueagi/das"
QUERY_AGENT_IMAGE_VERSION = "query-agent-0.10.3"

LINK_CREATION_AGENT_IMAGE_NAME = "trueagi/das"
LINK_CREATION_AGENT_IMAGE_VERSION = "link-creation-agent-0.10.3"

INFERENCE_AGENT_IMAGE_NAME = "trueagi/das"
INFERENCE_AGENT_IMAGE_VERSION = "inference-agent-0.10.3"

EVOLUTION_AGENT_IMAGE_NAME = "trueagi/das"
EVOLUTION_AGENT_IMAGE_VERSION = "evolution-agent-0.10.3"
