VERSION = '0.2.15'
RELEASE_NOTES_URL = (
    "https://raw.githubusercontent.com/singnet/das/master/docs/release-notes.md"
)

# PATHS

USER_DAS_PATH = "~/.das"

SECRETS_PATH = f"{USER_DAS_PATH}/config.json"

# SERVICES

REDIS_IMAGE_NAME = "redis"
REDIS_IMAGE_VERSION = "7.2.3-alpine"

MONGODB_IMAGE_NAME = "mongo"
MONGODB_IMAGE_VERSION = "6.0.13-jammy"

METTA_PARSER_IMAGE_NAME = "trueagi/das"
METTA_PARSER_IMAGE_VERSION = "0.3.6-metta-parser"

OPENFAAS_IMAGE_NAME = "trueagi/das"

JUPYTER_NOTEBOOK_IMAGE_NAME = "trueagi/das"
JUPYTER_NOTEBOOK_IMAGE_VERSION = "latest-jupyter-notebook"

# OTHERS

CLI_GROUP_NAME = "das"
CLI_USER_NAME = "das"
