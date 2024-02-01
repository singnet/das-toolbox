import os
import json
from typing import Any


class JsonHandler:
    def __init__(self, file_path):
        self._content = {}
        self._file_path = file_path
        self._load()

    def get_content(self) -> dict:
        return self._content

    def get_path(self) -> str:
        return self._file_path

    def is_ready(self) -> bool:
        return len(self.get_content().items()) > 0

    def _load(self):
        try:
            with open(self._file_path, "r") as config_file:
                self._content = json.load(config_file)
        except (FileNotFoundError, json.JSONDecodeError):
            self._content = {}

    def save(self):
        config_dir = os.path.dirname(self._file_path)
        os.makedirs(config_dir, exist_ok=True)

        with open(self._file_path, "w") as config_file:
            json.dump(self._content, config_file, indent=2)

    def get(self, key: str, default: Any = None):
        keys = key.split(".")
        current_dict = self._content

        for k in keys:
            current_dict = current_dict.get(k, {})

        return current_dict if current_dict else default

    def set(self, key: str, value: Any):
        keys = key.split(".")
        current_dict = self._content

        for k in keys[:-1]:
            current_dict = current_dict.setdefault(k, {})

        current_dict[keys[-1]] = value

        return self

    def append_to_array(self, key: str, value: Any):
        array = self.get(key, [])
        if not isinstance(array, list):
            raise ValueError(f"The key '{key}' does not correspond to an array.")

        array.append(value)

        self.set(key, array)

        return self

    def remove_from_array(self, key: str, value: Any):
        array = self.get(key, [])
        if not isinstance(array, list):
            raise ValueError(f"The key '{key}' does not correspond to an array.")

        try:
            array.remove(value)
            self.set(key, array)
        except ValueError:
            pass

        return self


class Config(JsonHandler):
    _default_config_path = os.path.expanduser("~/.das/config.json")

    def __init__(self):
        super().__init__(self._default_config_path)


class ContainerConfig(JsonHandler):
    _default_container_path = os.path.expanduser("~/.das/containers.json")

    def __init__(self):
        super().__init__(self._default_container_path)
