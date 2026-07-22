import getpass
import tempfile
from pathlib import Path

from common.config.loader import EnvFileLoader

VERSION = '1.1.0'
RELEASE_NOTES_URL = "https://raw.githubusercontent.com/singnet/das/master/docs/release-notes.md"

SERVICES_NETWORK_NAME = "host"

# PATHS

DAS_PATH = Path.home() / ".das"
SECRETS_PATH = DAS_PATH / ".env"

DEFAULT_CONFIGFILE_PATH = DAS_PATH / "config.json"
CURRENT_CONFIGFILE_PATH = (
    EnvFileLoader(SECRETS_PATH).load().get("configpath", DEFAULT_CONFIGFILE_PATH)
)

# LOG

LOG_FILE_NAME = Path(tempfile.gettempdir()) / f"{getpass.getuser()}-das-cli.log"

# SERVICES

REDIS_IMAGE_NAME = "redis"
REDIS_IMAGE_VERSION = "7.2.3-alpine"

MONGODB_IMAGE_NAME = "mongodb/mongodb-community-server"
MONGODB_IMAGE_VERSION = "8.0.4-ubuntu2204"

METTA_PARSER_IMAGE_NAME = "trueagi/das"
METTA_PARSER_IMAGE_VERSION = "1.0.0-metta-parser"

OPENFAAS_IMAGE_NAME = "trueagi/openfaas"

JUPYTER_NOTEBOOK_IMAGE_NAME = "trueagi/das"
JUPYTER_NOTEBOOK_IMAGE_VERSION = "latest-jupyter-notebook"

DAS_PEER_IMAGE_NAME = "trueagi/das"
DAS_PEER_IMAGE_VERSION = "latest-database-adapter-server"

DBMS_PEER_IMAGE_NAME = "trueagi/das"
DBMS_PEER_IMAGE_VERSION = "latest-database-adapter-client"

DAS_MORK_SERVER_IMAGE_NAME = "trueagi/das"
DAS_MORK_SERVER_IMAGE_VERSION = "mork-server-1.1.0"

DAS_MORK_LOADER_IMAGE_NAME = "trueagi/das"
DAS_MORK_LOADER_IMAGE_VERSION = "mork-loader-1.1.0"

DAS_IMAGE_VERSION = "1.1.0-rc"
DAS_IMAGE_NAME = "trueagi/das"
