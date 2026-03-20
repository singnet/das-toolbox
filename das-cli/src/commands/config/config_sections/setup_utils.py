from common.config.core import get_core_defaults_dict
from common.settings import Settings
from typing import Dict,Any

#########################################
##                MISC                 ##
#########################################

DEFAULT_VALUES_DICT = get_core_defaults_dict()

def extract_port(endpoint: str) -> int:
    try:
        return int(endpoint.split(":")[1])
    except Exception as e:
        raise ValueError(f"Invalid endpoint format: {endpoint}. Expected format: host:port") from e
    
def get_default_value(settings: Settings, path: str) -> Dict[str, Any]:
    existing_value = settings.get(path)

    if existing_value == None:
        keys = path.split(".")
        value = DEFAULT_VALUES_DICT

        for key in keys:
            value = value.get(key, None)
            if value is None:
                return None

        return value
    else:
        return existing_value