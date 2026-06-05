import json
import os
import subprocess
from collections import defaultdict
from pathlib import Path
from fastapi import UploadFile

from shared.internal.web_configuration import WebConfiguration
from shared.internal.constants import CONFIG_DIR, DEFAULT_WEBCONFIG_PATH
from shared.exceptions.custom_exceptions import DasCliCommandException


class ConfigServices:

    def __init__(self, web_config: WebConfiguration):
        self.web_config = web_config

    async def save_config(self, config_file: UploadFile):
        result = None
        try:
            os.makedirs(CONFIG_DIR, exist_ok=True)
            content = await config_file.read()

            with open(DEFAULT_WEBCONFIG_PATH, "wb") as f:
                f.write(content)

            result = subprocess.run(
                ["das-cli", "config", "set", "--file", DEFAULT_WEBCONFIG_PATH], 
                capture_output=True, 
                text=True, 
                check=True
            )

            loaded_json = await self.load_config()
            mapped_services = await self.map_services(loaded_json)

            self.web_config.config_dictionary = mapped_services

            stdout_content = result.stdout
            try:
                stdout_content = json.loads(result.stdout)
            except Exception:
                stdout_content = result.stdout.replace("\n", "").strip()

            return {"message": "Config applied", "stdout": stdout_content}

        except subprocess.CalledProcessError as e:
            error_output = (e.stderr or e.stdout or "Unknown Subprocess Error").strip()
            raise DasCliCommandException(error_output)
        
        except Exception as e:
            stderr_msg = result.stderr if (result and result.stderr) else str(e)
            raise DasCliCommandException(stderr_msg)

    async def load_config(self):
        try:
            with open(DEFAULT_WEBCONFIG_PATH, "r") as f:
                config_dict = json.load(f)

            if isinstance(config_dict, list):
                config_dict = config_dict[0]

            return config_dict
        except Exception:
            raise Exception("Error while trying to load config file.")

    def register_service(self, name: str, endpoint: str, services : dict):
        host, port = endpoint.split(":")
        services[name] = {
            "host": host,
            "port": int(port),
        }

    def map_atomdb(self, atomdb_section: dict, services : dict):
        mongodb_section : dict = atomdb_section.get("mongodb", None)
        redis_section = atomdb_section.get("redis", None)
        morkdb_section = atomdb_section.get("morkdb", None)

        if mongodb_section and redis_section:
            mongodb_endpoint = mongodb_section.get("endpoint")
            self.register_service("db", mongodb_endpoint, services)

        if mongodb_section and morkdb_section:
            mongodb_endpoint = mongodb_section.get("endpoint")
            self.register_service("db", mongodb_endpoint, services)
            
    async def map_services(self, config_file: dict):
        services = {}

        atomdb_section : dict = config_file.get("atomdb", None)

        if atomdb_section and atomdb_section.get("type") in ("redismongodb", "morkdb"):
            self.map_atomdb(atomdb_section, services)

        for key, value in config_file.get("brokers", {}).items():
            self.register_service(f"{key.replace('_', '-')}-broker", value["endpoint"], services)

        for key, value in config_file.get("agents", {}).items():
            self.register_service(f"{key.replace('_', '-')}-agent", value["endpoint"], services)

        return services