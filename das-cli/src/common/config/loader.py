from abc import ABC, abstractmethod
import os


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

    def load(self):
        data = {}
        if not os.path.exists(self._path):
            return data
        with open(self._path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    data[key.strip()] = value.strip().strip('"').strip("'")
        return data


class EnvVarLoader(ConfigLoader):
    def load(self):
        return dict(os.environ)
