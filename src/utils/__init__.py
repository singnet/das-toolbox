from .json_handler import JsonHandler
from .parsers import table_parser
from .network import (
    get_public_ip,
    get_server_username,
    get_ssh_user_and_ip,
    is_ssh_server_reachable,
    is_server_port_available,
)


def remove_special_characters(text):
    import re

    pattern = r"[^a-zA-Z0-9\s]"

    clean_text = re.sub(pattern, "", text)

    return clean_text.strip()
