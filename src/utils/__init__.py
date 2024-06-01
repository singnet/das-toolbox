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


def get_server_username() -> str:
    import getpass

    return getpass.getuser()


# TODO: validate ip
def get_ssh_user_and_ip(text: str) -> tuple:
    import re

    match = re.search(r"ssh:\/\/(\w+)@(\d{1,3}(?:\.\d{1,3}){3})(?::(\d+))?", text)

    if match:
        user = match.group(1)
        ip = match.group(2)

        return (user, ip)
    else:
        return None
