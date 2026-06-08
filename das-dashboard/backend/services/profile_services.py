import os
import json
from pathlib import Path
from fastapi import UploadFile

from shared.exceptions.custom_exceptions import ProfileSaveException
from shared.internal.web_configuration import WebConfiguration
from shared.internal.constants import CONFIG_DIR, DEFAULT_SSHKEY_CLONE_PATH, DEFAULT_WEBPROFILE_PATH


class ProfileServices:

    def __init__(self, web_config: WebConfiguration):
        self.web_config = web_config

    def load_dashboard_profile_safe(self) -> dict | None:
        if not os.path.exists(DEFAULT_WEBPROFILE_PATH):
            return None

        try:
            with open(DEFAULT_WEBPROFILE_PATH, "r") as f:
                return json.load(f)
        except Exception:
            return None

    async def save_dashboard_profile(self, username: str, key_file: UploadFile) -> str:
        try:
            os.makedirs(CONFIG_DIR, exist_ok=True)
            content = await key_file.read()

            with open(DEFAULT_SSHKEY_CLONE_PATH, "wb") as f:
                f.write(content)
            os.chmod(DEFAULT_SSHKEY_CLONE_PATH, 0o400)

            profile_data = {
                "profile_username": username,
                "profile_ssh_keypath": DEFAULT_SSHKEY_CLONE_PATH,
            }

            with open(DEFAULT_WEBPROFILE_PATH, "w") as f:
                json.dump(profile_data, f, indent=4)

            self.web_config.user_profile = profile_data
            return "Profile saved successfully."

        except Exception as e:
            raise ProfileSaveException(
                error_message=f"Failed to save the profile configuration. Details: {str(e)}"
            )