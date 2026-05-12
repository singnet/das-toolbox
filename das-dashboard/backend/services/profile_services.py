from shared.dtos.dashboard_profile_dto import DashboardProfileDto

from shared.exceptions.custom_exceptions import ProfileSaveException, ProfileNotFoundException

import os
import json


EXPANDED_HOME = os.path.expanduser("~")

DEFAULT_PROFILE_PATH = os.path.join(
    EXPANDED_HOME,
    ".das",
    "webapp_profile.json"
)

DEFAULT_KEY_CLONE_PATH = os.path.join(EXPANDED_HOME, ".das", ".remote_key")

DEFAULT_CONFIG_PATH = os.path.join(
    EXPANDED_HOME,
    ".das",
    ".env"
)

class ProfileServices:

    def load_profile_and_config():
        pass

    def _remove_old_profile(self, previous_profile):
        old_key_path = previous_profile.get("profile_ssh_keypath")

        if old_key_path and os.path.exists(old_key_path):
            os.remove(old_key_path)

    async def _save_ssh_copy(self, request):
        
        content = await request.sshKeyFile.read()

        with open(DEFAULT_KEY_CLONE_PATH, "wb") as key_file:
            key_file.write(content)
            key_file.close()

        os.chmod(DEFAULT_KEY_CLONE_PATH, 0o400)

    def load_dashboard_profile_safe(self) -> dict | None:
        if not os.path.exists(DEFAULT_PROFILE_PATH):
            return None

        try:
            with open(DEFAULT_PROFILE_PATH, "r") as file:
                return json.load(file)
            
        except FileNotFoundError:
            return ProfileNotFoundException(f"No profile was found at: {DEFAULT_PROFILE_PATH}")


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

            return;
        except Exception:
            raise ProfileSaveException("An internal I/O error prevented the profile from being saved.")