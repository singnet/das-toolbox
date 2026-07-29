import json
import os
from abc import ABC, abstractmethod
from typing import Any, Dict

from common.utils import deep_merge_dicts
from settings.config import CURRENT_CONFIGFILE_PATH


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
    def set_path(self, new_file_path) -> None:
        """Set the new configuration file path or identifier."""
        pass

    def save_path(self) -> None:
        """Save the new configuration file path of identifier."""
        pass

    @abstractmethod
    def get_dir_path(self) -> str:
        """Get the directory path where the configuration is stored."""
        pass


class JsonConfigStore(ConfigStore):
    def __init__(self, env_file_path: str):
        self._file_path = CURRENT_CONFIGFILE_PATH
        self._env_path = env_file_path
        self._content: Dict[str, Any] = {}
        self._new_content: Dict[str, Any] = {}
        self._overwrite_mode = False
        self._load_error: Exception | None = None
        self.rewind()

    def get_content(self) -> dict:
        return {**self._content, **self._new_content}

    def set_content(self, content: Dict[str, Any]) -> None:
        self._new_content = content

    def get_path(self) -> str:
        return self._file_path

    def set_path(self, new_file_path: str) -> None:
        self._file_path = new_file_path

    def save_path(self) -> None:
        os.makedirs(os.path.dirname(self._env_path), exist_ok=True)
        with open(self._env_path, "w", encoding="utf-8") as env_file:
            env_file.write(f"configpath={self._file_path}\n")

    def get_dir_path(self) -> str:
        return os.path.dirname(self._file_path)

    def file_exists(self) -> bool:
        return bool(self._file_path) and os.path.isfile(self._file_path)

    def exists(self) -> bool:
        return isinstance(self.get_content(), dict) and len(self.get_content()) > 0

    def rewind(self):
        self._new_content = {}
        try:
            with open(self._file_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            if not isinstance(loaded, dict):
                raise json.JSONDecodeError(
                    "Configuration root must be a JSON object",
                    doc=str(self._file_path),
                    pos=0,
                )
            self._content = loaded
            self._load_error = None
        except FileNotFoundError as error:
            self._content = {}
            self._load_error = error
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            self._content = {}
            self._load_error = error
        except OSError as error:
            self._content = {}
            self._load_error = error

        return self

    def get_load_error(self) -> Exception | None:
        return self._load_error

    def enable_overwrite_mode(self):
        self._overwrite_mode = True
        self._content = {}
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

        if not self._file_path:
            raise RuntimeError("Config path not defined")

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
