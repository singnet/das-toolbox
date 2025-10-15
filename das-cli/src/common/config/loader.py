import os
from abc import ABC, abstractmethod
from typing import Dict, Any
import click
from common.execution_context import ExecutionContext


class ConfigLoader(ABC):
    @abstractmethod
    def load(self) -> dict:
        pass


class CompositeLoader(ConfigLoader):
    def __init__(self, loaders: list[ConfigLoader]):
        self._loaders = loaders

    def load(self):
        result = {}
        for loader in self._loaders:
            data = loader.load()
            result.update(data)
        return result


class EnvFileLoader(ConfigLoader):
    def __init__(self, path: str):
        self._path = path

    def _format_key(self, key: str) -> str:
        return key.strip().lower().replace("_", ".").replace("das", "services")

    def _format_value(self, value: str) -> str:
        return value.strip().strip('"').strip("'")

    def load(self):
        data: Dict[str, str] = {}
        if not self._path or not os.path.exists(self._path):
            return data
        with open(self._path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    f_key = self._format_key(key)
                    f_value = self._format_value(value)

                    data[f_key] = f_value
        return data


class EnvVarLoader(ConfigLoader):
    def _format_key(self, key: str) -> str:
        return key.strip().lower().replace("_", ".").replace("das", "services")

    def _format_value(self, value: str) -> str:
        return value.strip().strip('"').strip("'")

    def load(self):
        data = {}
        for key, value in dict(os.environ).items():
            if key.startswith("DAS"):
                f_key = self._format_key(key)
                f_value = self._format_value(value)
                data[f_key] = f_value

        return data

class ContextLoader(ConfigLoader):
    def __init__(self):
        ctx = click.get_current_context(silent=True)
        self._execution_context: ExecutionContext | None = None

        if ctx and ctx.obj and "execution_context" in ctx.obj:
            self._execution_context = ctx.obj["execution_context"]

    def load(self) -> Dict[str, Any]:
        if not self._execution_context:
            return {}

        overrides = {}

        ctx_data = self._execution_context.context
        for key, value in ctx_data.items():
            overrides[key] = value

        return overrides