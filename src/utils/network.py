import subprocess
from typing import Union


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


def is_server_port_available(host, start_port, end_port):
    for port in range(start_port, end_port + 1):
        command = f"nc -zv {host} {port}"
        result = subprocess.call(command, shell=True)

        if result != 0:
            return False

    return True


def is_ssh_server_reachable(server: dict) -> bool:
    command = f'ssh -q -o BatchMode=yes -o ConnectTimeout=5 {server["username"]}@{server["ip"]} "echo 2>&1"'
    ping = subprocess.call(command, shell=True)

    return ping == 0
