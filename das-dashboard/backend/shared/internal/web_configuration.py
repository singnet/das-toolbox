import json
import os
from pathlib import Path

CONFIG_DIR = os.path.join(Path.home(), ".das")

PROFILE_PATH = os.path.join(CONFIG_DIR, "web_profile.json")
CONFIG_PATH = os.path.join(CONFIG_DIR, "webconfig.json")

class WebConfiguration:

    _instance = None
    config_dictionary: dict[str, str] = {}
    user_profile: dict[str, str] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load_user_profile(self):
        if not os.path.exists(PROFILE_PATH):
            self.user_profile = {}
            return

        try:
            with open(PROFILE_PATH, "r") as f:
                self.user_profile = json.load(f)
        except:
            self.user_profile = {}

    def load_config_dictionary(self):
        if not os.path.exists(CONFIG_PATH):
            self.config_dictionary = {}
            return

        try:
            with open(CONFIG_PATH, "r") as f:
                config = json.load(f)

            if isinstance(config, list):
                config = config[0]

            self.config_dictionary = self.map_services(config)
        except:
            self.config_dictionary = {}

    def map_services(self, config_file: dict):
        services = {}

        def register(name: str, endpoint: str):
            host, port = endpoint.split(":")
            services[name] = {
                "host": host,
                "port": int(port),
            }

        atomdb_section = config_file.get("atomdb", None)
        if atomdb_section and atomdb_section.get("type") in ("redismongodb", "morkdb"):
            mongodb_section = atomdb_section.get("mongodb", None)
            redis_section = atomdb_section.get("redis", None)
            morkdb_section = atomdb_section.get("morkdb", None)

            if (mongodb_section and redis_section) or (mongodb_section and morkdb_section):
                mongodb_endpoint = mongodb_section.get("endpoint")
                register("db", mongodb_endpoint)

        for key, value in config_file.get("brokers", {}).items():
            register(f"{key.replace('_', '-')}-broker", value["endpoint"])

        for key, value in config_file.get("agents", {}).items():
            register(f"{key.replace('_', '-')}-agent", value["endpoint"])

        return services