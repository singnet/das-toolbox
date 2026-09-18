from copy import deepcopy
from typing import Any, Dict

from common.config.defaults import get_default_config_schema_dict


def get_core_schema_dict() -> Dict[str, Any]:
    return get_default_config_schema_dict()


def get_core_defaults_dict() -> Dict[str, Any]:
    return deepcopy(get_core_schema_dict())
