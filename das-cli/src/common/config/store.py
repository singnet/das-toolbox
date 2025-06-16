import json
import os
from abc import ABC, abstractmethod
from typing import Any


class ConfigStore(ABC):
    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from the configuration by dotted key path."""
        pass

    @abstractmethod
    def set(self, key: str, value: Any):
        """Set a value in the configuration by dotted key path."""
        pass

    @abstractmethod
    def save(self):
        """Persist the current configuration to disk (or storage)."""
        pass

    @abstractmethod
    def rewind(self):
        """Reload configuration content from the source (e.g., file)."""
        pass

    @abstractmethod
    def exists(self) -> bool:
        """Check if configuration exists (has content)."""
        pass

    @abstractmethod
    def get_content(self) -> dict:
        """Get the entire configuration content as a dict."""
        pass

    @abstractmethod
    def get_path(self) -> str:
        """Get the configuration file path or storage identifier."""
        pass

    @abstractmethod
    def get_dir_path(self) -> str:
        """Get the directory path where the configuration is stored."""
        pass


class JsonConfigStore(ConfigStore):
    def __init__(self, file_path):
        self._content = {}
        self._file_path = file_path
        self.rewind()

    def get_content(self) -> dict:
        return self._content

    def get_path(self) -> str:
        return self._file_path

    def get_dir_path(self) -> str:
        return os.path.dirname(self._file_path)

    def exists(self) -> bool:
        return len(self.get_content().items()) > 0

    def rewind(self):
        try:
            with open(self._file_path, "r") as config_file:
                self._content = json.load(config_file)
        except (FileNotFoundError, json.JSONDecodeError):
            self._content = {}

        return self

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
