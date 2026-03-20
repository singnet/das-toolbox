from common.config.core import get_core_defaults_dict
from typing import Dict,Any

#########################################
##                MISC                 ##
#########################################

DEFAULT_VALUES_DICT = get_core_defaults_dict()

def _extract_port(endpoint: str) -> int:
    try:
        return int(endpoint.split(":")[1])
    except Exception as e:
        raise ValueError(f"Invalid endpoint format: {endpoint}. Expected format: host:port") from e
    
def _get_default_value(path: str) -> Dict[str, Any]:
    keys = path.split(".")
    value = DEFAULT_VALUES_DICT

    for key in keys:
        value = value.get(key, None)
        if value is None:
            return None

    return value