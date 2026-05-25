import os
from pathlib import Path



CONFIG_DIR = os.path.join(Path.home(), ".das")

DEFAULT_WEBCONFIG_PATH = os.path.join(CONFIG_DIR, "webconfig.json")
DEFAULT_WEBPROFILE_PATH = os.path.join(CONFIG_DIR, "web_profile.json")
DEFAULT_SSHKEY_CLONE_PATH = os.path.join(CONFIG_DIR, "web_key")
DEFAULT_METTA_FILES_PATH = os.path.join(CONFIG_DIR, "metta_files/")