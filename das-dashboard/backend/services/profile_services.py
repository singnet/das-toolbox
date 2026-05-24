import os
import json

from pathlib import Path
from fastapi import UploadFile

from shared.exceptions.custom_exceptions import ProfileSaveException
from shared.internal.web_configuration import WebConfiguration


CONFIG_DIR = os.path.join(Path.home(), ".das")
PROFILE_PATH = os.path.join(CONFIG_DIR, "web_profile.json")
KEY_CLONE_PATH = os.path.join(CONFIG_DIR, "web_key")


class ProfileServices:

    def __init__(self, web_config: WebConfiguration):
        self.web_config = web_config

    def load_dashboard_profile_safe(self) -> dict | None:

        if not os.path.exists(PROFILE_PATH):
            return None

        try:
            with open(PROFILE_PATH, "r") as f:
                return json.load(f)

        except:
            return None

    async def save_dashboard_profile(self, username: str, key_file: UploadFile) -> str:

        try:

            os.makedirs(CONFIG_DIR, exist_ok=True)
            content = await key_file.read()

            with open(KEY_CLONE_PATH, "wb") as f:
                f.write(content)
            os.chmod(KEY_CLONE_PATH, 0o400)

            profile_data = {
                "profile_username": username,
                "profile_ssh_keypath": KEY_CLONE_PATH,
            }

            with open(PROFILE_PATH, "w") as f:
                json.dump(profile_data, f)

            self.web_config.user_profile = profile_data
            return "Profile saved successfully"

        except Exception as e:
            raise ProfileSaveException(str(e))