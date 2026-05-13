import os
import json
import subprocess

from fastapi import UploadFile

from shared.dtos.dashboard_profile_dto import DashboardProfileDto
from shared.exceptions.custom_exceptions import ProfileSaveException, ProfileNotFoundException


CONFIG_DIR = "/opt/das/.das"
UPLOAD_CONFIG_PATH = os.path.join(CONFIG_DIR, "webconfig.json")
DEFAULT_PROFILE_PATH = os.path.join(CONFIG_DIR, "webapp_profile.json")
DEFAULT_KEY_CLONE_PATH = os.path.join(CONFIG_DIR, ".remote_key")


class ProfileServices:

    async def save_config(self, config_file: UploadFile):
        try:
            os.makedirs(CONFIG_DIR, exist_ok=True)

            await config_file.seek(0)
            content = await config_file.read()

            if not content:
                raise Exception("No content received from frontend")

            with open(UPLOAD_CONFIG_PATH, "wb") as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())

            result = subprocess.run(
                ["das-cli", "config", "set", "--file", UPLOAD_CONFIG_PATH],
                capture_output=True,
                text=True,
                check=True
            )

            return {
                "message": "Config applied",
                "stdout": result.stdout
            }

        except subprocess.CalledProcessError as e:
            raise Exception(f"CLI Error: {e.stderr}")
        except Exception as e:
            raise Exception(f"IO Error: {str(e)}")

    def _remove_old_profile(self, previous_profile):
        old_key_path = previous_profile.get("profile_ssh_keypath")
        if old_key_path and os.path.exists(old_key_path):
            os.remove(old_key_path)

    async def _save_ssh_copy(self, request):
        await request.sshKeyFile.seek(0)
        content = await request.sshKeyFile.read()

        with open(DEFAULT_KEY_CLONE_PATH, "wb") as key_file:
            key_file.write(content)
            key_file.flush()
            os.fsync(key_file.fileno())

        os.chmod(DEFAULT_KEY_CLONE_PATH, 0o400)

    def load_dashboard_profile_safe(self) -> dict | None:
        if not os.path.exists(DEFAULT_PROFILE_PATH):
            return None

        try:
            with open(DEFAULT_PROFILE_PATH, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    async def save_dashboard_profile(self, request: DashboardProfileDto) -> str:
        try:
            os.makedirs(CONFIG_DIR, exist_ok=True)
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
                profile_file.flush()
                os.fsync(profile_file.fileno())

            return "Profile saved successfully"

        except Exception:
            raise ProfileSaveException(
                "An internal I/O error prevented the profile from being saved."
            )