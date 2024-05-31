from .json_handler import JsonHandler
from .parsers import table_parser


def remove_special_characters(text):
    import re

    pattern = r"[^a-zA-Z0-9\s]"

    clean_text = re.sub(pattern, "", text)

    return clean_text.strip()


def get_public_ip():
    import requests

    try:
        return requests.get("https://api.ipify.org").content.decode("utf8")
    except:
        return None


def get_server_username():
    import getpass

    return getpass.getuser()
