import os

# Shared root mounted on host and container (-v /opt/web-das:/opt/web-das).
# Do not use Path.home() — das-cli resolves ~/.das from the process HOME, which
# may be /root inside the container while the host user is /home/USERNAME, etc.
SHARED_DAS_ROOT = os.environ.get("DAS_SHARED_ROOT", "/opt/web-das")
CONFIG_DIR = os.path.join(SHARED_DAS_ROOT, ".das")

CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")
QUERY_DB_PATH = os.path.join(CONFIG_DIR, "query_responses.db")
DEFAULT_WEBPROFILE_PATH = os.path.join(CONFIG_DIR, "web_profile.json")
DEFAULT_SSHKEY_CLONE_PATH = os.path.join(CONFIG_DIR, "web_key")
ADAPTER_CONTEXT_MAPPING_FILE = os.path.join(CONFIG_DIR, "adapter_context_mapping.sql")

WORKSPACE_ROOT = os.path.join(CONFIG_DIR, "workspace")
WORKSPACE_METTA_OUTPUT = os.path.join(WORKSPACE_ROOT, "mapped_metta")
DEFAULT_METTA_FILES_PATH = os.path.join(WORKSPACE_ROOT, "metta_files")

REMOTE_WORKSPACE_ROOT = "/.das/workspace"
REMOTE_METTA_FILES_PATH = f"{REMOTE_WORKSPACE_ROOT}/metta_files"
REMOTE_CONFIG_PATH = "/.das/config.json"

LOCAL_HOSTS = frozenset({"localhost", "127.0.0.1", "0.0.0.0"})
LOCAL_DASHBOARD_HOST = "localhost"
