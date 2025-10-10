import getpass
from pathlib import Path
import tempfile

VERSION = '0.5.5'
RELEASE_NOTES_URL = "https://raw.githubusercontent.com/singnet/das/master/docs/release-notes.md"

SERVICES_NETWORK_NAME = "das-services-network"

# PATHS

USER_DAS_PATH = Path.home() / ".das"

SECRETS_PATH = USER_DAS_PATH / "config.json"

# LOG

LOG_FILE_NAME = Path(tempfile.gettempdir()) / f"{getpass.getuser()}-das-cli.log"

# SERVICES

REDIS_IMAGE_NAME = "redis"
REDIS_IMAGE_VERSION = "7.2.3-alpine"

MONGODB_IMAGE_NAME = "mongo"
MONGODB_IMAGE_VERSION = "6.0.13-jammy"

METTA_PARSER_IMAGE_NAME = "trueagi/das"
METTA_PARSER_IMAGE_VERSION = "0.5.9-metta-parser"

OPENFAAS_IMAGE_NAME = "trueagi/openfaas"

JUPYTER_NOTEBOOK_IMAGE_NAME = "trueagi/das"
JUPYTER_NOTEBOOK_IMAGE_VERSION = "latest-jupyter-notebook"

DAS_PEER_IMAGE_NAME = "trueagi/das"
DAS_PEER_IMAGE_VERSION = "latest-database-adapter-server"

DBMS_PEER_IMAGE_NAME = "trueagi/das"
DBMS_PEER_IMAGE_VERSION = "latest-database-adapter-client"

DAS_VERSION = "0.11.7"

ATTENTION_BROKER_IMAGE_NAME = "trueagi/das"
ATTENTION_BROKER_IMAGE_VERSION = f"attention-broker-{DAS_VERSION}"

QUERY_AGENT_IMAGE_NAME = "trueagi/das"
QUERY_AGENT_IMAGE_VERSION = f"query-agent-{DAS_VERSION}"

LINK_CREATION_AGENT_IMAGE_NAME = "trueagi/das"
LINK_CREATION_AGENT_IMAGE_VERSION = f"link-creation-agent-{DAS_VERSION}"

INFERENCE_AGENT_IMAGE_NAME = "trueagi/das"
INFERENCE_AGENT_IMAGE_VERSION = f"inference-agent-{DAS_VERSION}"

EVOLUTION_AGENT_IMAGE_NAME = "trueagi/das"
EVOLUTION_AGENT_IMAGE_VERSION = f"evolution-agent-{DAS_VERSION}"

CONTEXT_BROKER_IMAGE_NAME = "trueagi/das"
CONTEXT_BROKER_IMAGE_VERSION = f"context-broker-{DAS_VERSION}"
