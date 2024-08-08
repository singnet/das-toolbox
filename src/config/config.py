from common.utils import get_server_username


VERSION = '0.3.1'
RELEASE_NOTES_URL = (
    "https://raw.githubusercontent.com/singnet/das/master/docs/release-notes.md"
)

# PATHS

USER_DAS_PATH = "~/.das"

SECRETS_PATH = f"{USER_DAS_PATH}/config.json"

# LOG

LOG_FILE_DIR = get_server_username()
LOG_FILE_NAME = f"/tmp/{LOG_FILE_DIR}-das-cli.log"

# SERVICES

REDIS_IMAGE_NAME = "redis"
REDIS_IMAGE_VERSION = "7.2.3-alpine"

MONGODB_IMAGE_NAME = "mongo"
MONGODB_IMAGE_VERSION = "6.0.13-jammy"

METTA_PARSER_IMAGE_NAME = "trueagi/das"
METTA_PARSER_IMAGE_VERSION = "0.4.1-metta-parser"

OPENFAAS_IMAGE_NAME = "trueagi/openfaas"

JUPYTER_NOTEBOOK_IMAGE_NAME = "trueagi/das"
JUPYTER_NOTEBOOK_IMAGE_VERSION = "latest-jupyter-notebook"
