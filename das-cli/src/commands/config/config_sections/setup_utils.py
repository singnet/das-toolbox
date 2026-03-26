from typing import Any, Dict

from common.config.core import get_core_defaults_dict
from common.settings import Settings

DEFAULT_VALUES_DICT = get_core_defaults_dict()


def get_default_value(settings: Settings, path: str) -> str | Dict[str, Any] | None:
    existing_value = settings.get(path)

    if existing_value is None:
        try:
            keys = path.split(".")
            value = DEFAULT_VALUES_DICT

            for key in keys:
                value = value.get(key, None)
                if value is None:
                    return None
        except AttributeError:
            return None

        return value
    else:
        return existing_value
