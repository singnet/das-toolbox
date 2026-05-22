from fastapi import UploadFile
from pathlib import Path
from collections import defaultdict
import json
import os
import subprocess
from shared.internal.web_configuration import WebConfiguration

CONFIG_DIR = os.path.join(Path.home(), ".das")
UPLOAD_CONFIG_PATH = os.path.join(CONFIG_DIR, "webconfig.json")

class ConfigServices:

    def __init__(self, web_config: WebConfiguration):
        self.web_config = web_config

    async def save_config(self, config_file: UploadFile):
        try:
            os.makedirs(CONFIG_DIR, exist_ok=True)
            content = await config_file.read()

            with open(UPLOAD_CONFIG_PATH, "wb") as f:
                f.write(content)

            result = subprocess.run(
                ["das-cli", "config", "set", "--file", UPLOAD_CONFIG_PATH], 
                capture_output=True, 
                text=True, 
                check=True
            )

            loaded_json = await self.load_config()
            mapped_servers = await self.map_servers_services(loaded_json)

            self.web_config.config_dictionary = mapped_servers

            return {"message": "Config applied", "stdout": result.stdout}

        except Exception as e:
            raise Exception(f"Failed to apply config: {str(e)}")

    async def load_config(self):
        try:
            with open(UPLOAD_CONFIG_PATH, "r") as f:
                config_dict = json.load(f)

            if isinstance(config_dict, list):
                config_dict = config_dict[0]

            return config_dict
        except Exception:
            raise Exception("Error while trying to load config file.")
