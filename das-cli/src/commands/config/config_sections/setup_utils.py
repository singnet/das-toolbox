from typing import Any, Dict

from common.config.defaults import get_default_config_dict
from common.settings import Settings


def _default_values_dict() -> Dict[str, Any]:
    try:
        return get_default_config_dict()
    except (FileNotFoundError, ValueError):
        return {}


def get_default_value(settings: Settings, path: str) -> str | Dict[str, Any] | None:
    existing_value = settings.get(path)

    if existing_value is None:
        try:
            keys = path.split(".")
            value: Any = _default_values_dict()

            for key in keys:
                value = value.get(key, None)
                if value is None:
                    return None
        except AttributeError:
            return None

        return value
    else:
        return existing_value
