import json
import os
from abc import ABC, abstractmethod
from typing import Any, Dict

from common.utils import deep_merge_dicts


class ConfigStore(ABC):
    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from the configuration by dotted key path."""
        pass

    @abstractmethod
    def enable_overwrite_mode(self):
        """
        Enable overwrite mode for the configuration store.

        When overwrite mode is enabled, the next save operation will ignore any
        previously loaded content from the existing configuration file (if any)
        and will persist only the newly set values. This is useful when you want
        to create or reset a configuration file from scratch, without merging
        with old keys or values.

        Typical use cases:
        - Creating a brand new configuration file.
        - Resetting an existing configuration file to a clean state.
        """
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
    def set_content(self, content: Dict[str, Any]) -> None:
        """Set the entire configuration content"""
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
    def __init__(self, file_path: str):
        self._file_path = file_path
        self._content: Dict[str, Any] = {}
        self._new_content: Dict[str, Any] = {}
        self._overwrite_mode = False
        self.rewind()

    def get_content(self) -> dict:
        return {**self._content, **self._new_content}

    def set_content(self, content: Dict[str, Any]) -> None:
        self._new_content = content

    def get_path(self) -> str:
        return self._file_path

    def get_dir_path(self) -> str:
        return os.path.dirname(self._file_path)

    def exists(self) -> bool:
        return len(self.get_content().items()) > 0

    def rewind(self):
        try:
            with open(self._file_path, "r") as f:
                self._content = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._content = {}
        return self

    def enable_overwrite_mode(self):
        self._overwrite_mode = True
        self._new_content = {}
        return self

    def get(self, key: str, default: Any = None):
        keys = key.split(".")
        current_dict = deep_merge_dicts(self._content, self._new_content)

        for k in keys:
            current_dict = current_dict.get(k, {})

        return current_dict if current_dict else default

    def set(self, key: str, value: Any):
        keys = key.split(".")
        current = self._new_content
        for k in keys[:-1]:
            current = current.setdefault(k, {})
        current[keys[-1]] = value
        return self

    def save(self):
        os.makedirs(os.path.dirname(self._file_path), exist_ok=True)

        if self._overwrite_mode:
            data_to_save = self._new_content
        else:
            data_to_save = self.get_content()

        with open(self._file_path, "w") as f:
            json.dump(data_to_save, f, indent=2)

        self._content = data_to_save
        self._new_content = {}
        self._overwrite_mode = False
