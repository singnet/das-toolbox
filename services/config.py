import json
import os
from typing import Any

DEFAULT_CONFIG_PATH = os.path.expanduser("~/.das/config.json")


class ConfigService:
    def __init__(self, config_path=DEFAULT_CONFIG_PATH):
        self.config_path = os.path.expanduser(config_path)
        self.config = {}

    def load(self):
        try:
            with open(self.config_path, "r") as config_file:
                self.config = json.load(config_file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.config = {}

    def save(self):
        config_dir = os.path.dirname(self.config_path)
        os.makedirs(config_dir, exist_ok=True)

        with open(self.config_path, "w") as config_file:
            json.dump(self.config, config_file, indent=2)

    def get(self, key: str, default: Any = None):
        keys = key.split(".")
        current_dict = self.config

        for k in keys:
            current_dict = current_dict.get(k, {})

        return current_dict if current_dict else default

    def set(self, key: str, value: Any):
        keys = key.split(".")
        current_dict = self.config

        for k in keys[:-1]:
            current_dict = current_dict.setdefault(k, {})

        current_dict[keys[-1]] = value
