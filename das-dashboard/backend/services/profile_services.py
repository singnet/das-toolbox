import os
import json
from fastapi import UploadFile
from pathlib import Path
from shared.exceptions.custom_exceptions import ProfileSaveException

CONFIG_DIR = os.path.join(Path.home(), ".das")
PROFILE_PATH = os.path.join(CONFIG_DIR, "web_profile.json")
KEY_CLONE_PATH = os.path.join(CONFIG_DIR, "web_key")

class ProfileServices:

    def __init__(self):
        pass

    def load_dashboard_profile_safe(self) -> dict | None:
        if not os.path.exists(PROFILE_PATH): return None
        try:
            with open(PROFILE_PATH, "r") as f:
                return json.load(f)
        except: return None

    async def save_dashboard_profile(self, username: str, key_file: UploadFile) -> str:
        try:
            os.makedirs(CONFIG_DIR, exist_ok=True)
            
            content = await key_file.read()
            with open(KEY_CLONE_PATH, "wb") as f:
                f.write(content)
            os.chmod(KEY_CLONE_PATH, 0o400)

            profile_data = {"profile_username": username, "profile_ssh_keypath": KEY_CLONE_PATH}
            with open(PROFILE_PATH, "w") as f:
                json.dump(profile_data, f)
            
            return "Profile saved successfully"
        except Exception:
            raise ProfileSaveException("I/O error during profile save.")