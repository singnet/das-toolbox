import os
import json
import subprocess

from fastapi import UploadFile

from shared.dtos.dashboard_profile_dto import DashboardProfileDto
from shared.exceptions.custom_exceptions import ProfileSaveException, ProfileNotFoundException


EXPANDED_HOME = os.path.expanduser("~")

DEFAULT_PROFILE_PATH = os.path.join(
    EXPANDED_HOME,
    ".das",
    "webapp_profile.json"
)

DEFAULT_KEY_CLONE_PATH = os.path.join(
    EXPANDED_HOME,
    ".das",
    ".remote_key"
)

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".das")
CONFIG_PATH = os.path.join(CONFIG_DIR, "webconfig.json")

class ProfileServices:

    async def save_config(self, config_file: UploadFile):

        try:
            os.makedirs(CONFIG_DIR, exist_ok=True)

            content = await config_file.read()

            with open(CONFIG_PATH, "wb") as f:
                f.write(content)

            subprocess.run(
                ["das-cli", "config", "set", "--file", CONFIG_PATH],
                check=True
            )

            return {
                "message": "Config saved and applied successfully",
                "config_path": CONFIG_PATH
            }

        except Exception as e:
            raise Exception(f"Failed to save/apply config: {str(e)}")

    def _remove_old_profile(self, previous_profile):
        old_key_path = previous_profile.get("profile_ssh_keypath")

        if old_key_path and os.path.exists(old_key_path):
            os.remove(old_key_path)

    async def _save_ssh_copy(self, request):
        content = await request.sshKeyFile.read()

        with open(DEFAULT_KEY_CLONE_PATH, "wb") as key_file:
            key_file.write(content)

        os.chmod(DEFAULT_KEY_CLONE_PATH, 0o400)

    def load_dashboard_profile_safe(self) -> dict | None:
        if not os.path.exists(DEFAULT_PROFILE_PATH):
            return None

        try:
            with open(DEFAULT_PROFILE_PATH, "r") as file:
                return json.load(file)

        except FileNotFoundError:
            raise ProfileNotFoundException(
                f"No profile was found at: {DEFAULT_PROFILE_PATH}"
            )

    async def save_dashboard_profile(self, request: DashboardProfileDto) -> str:
        try:
            previous_profile = self.load_dashboard_profile_safe()

            if previous_profile:
                self._remove_old_profile(previous_profile)

            await self._save_ssh_copy(request)

            profile_json = {
                "profile_username": request.sshUsername,
                "profile_ssh_keypath": DEFAULT_KEY_CLONE_PATH,
            }

            with open(DEFAULT_PROFILE_PATH, "w") as profile_file:
                json.dump(profile_json, profile_file)

        except Exception:
            raise ProfileSaveException(
                "An internal I/O error prevented the profile from being saved."
            )