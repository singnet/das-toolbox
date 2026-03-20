from common.utils import search_dict_key
from common.settings import Settings

def safe_extract_value(settings: Settings, default:dict ,key: str):
    value = settings.get(key)

    if value == None:
        value = search_dict_key(default, key)
        return value
    
    else:
        return value
    
def extract_port(endpoint:str):
    return endpoint.split(":")[1]