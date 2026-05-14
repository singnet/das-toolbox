import os
import json
import subprocess
from fastapi import UploadFile
from shared.exceptions.custom_exceptions import ProfileSaveException

CONFIG_DIR = "/opt/das/.das"
UPLOAD_CONFIG_PATH = os.path.join(CONFIG_DIR, "webconfig.json")
DEFAULT_PROFILE_PATH = os.path.join(CONFIG_DIR, "webapp_profile.json")
DEFAULT_KEY_CLONE_PATH = os.path.join(CONFIG_DIR, ".remote_key")

class ProfileServices:
    async def save_config(self, config_file: UploadFile):
        try:
            os.makedirs(CONFIG_DIR, exist_ok=True)
            content = await config_file.read()
            
            with open(UPLOAD_CONFIG_PATH, "wb") as f:
                f.write(content)
            
            result = subprocess.run(
                ["das-cli", "config", "set", "--file", UPLOAD_CONFIG_PATH],
                capture_output=True, text=True, check=True
            )
            return {"message": "Config applied", "stdout": result.stdout}
        except Exception as e:
            raise Exception(f"Failed to apply config: {str(e)}")

    def load_dashboard_profile_safe(self) -> dict | None:
        if not os.path.exists(DEFAULT_PROFILE_PATH): return None
        try:
            with open(DEFAULT_PROFILE_PATH, "r") as f:
                return json.load(f)
        except: return None

    async def save_dashboard_profile(self, username: str, key_file: UploadFile) -> str:
        try:
            os.makedirs(CONFIG_DIR, exist_ok=True)
            
            content = await key_file.read()
            with open(DEFAULT_KEY_CLONE_PATH, "wb") as f:
                f.write(content)
            os.chmod(DEFAULT_KEY_CLONE_PATH, 0o400)

            profile_data = {"profile_username": username, "profile_ssh_keypath": DEFAULT_KEY_CLONE_PATH}
            with open(DEFAULT_PROFILE_PATH, "w") as f:
                json.dump(profile_data, f)
            
            return "Profile saved successfully"
        except Exception:
            raise ProfileSaveException("I/O error during profile save.")