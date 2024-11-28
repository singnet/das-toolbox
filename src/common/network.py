import re
import subprocess
from typing import Union

import requests


def get_public_ip():
    try:
        return requests.get("https://api.ipify.org").content.decode("utf8")
    # TODO: better exception handler, for now do not use bare except
    except Exception:
        return None


# TODO: validate ip
def get_ssh_user_and_ip(text: str) -> tuple:
    match = re.search(r"ssh:\/\/(\w+)@(\d{1,3}(?:\.\d{1,3}){3})(?::(\d+))?", text)

    if match:
        user = match.group(1)
        ip = match.group(2)

        return (user, ip)
    else:
        return None


def is_server_port_available(
    username: str,
    host: str,
    start_port: int,
    end_port: Union[int, None] = None,
):
    def server_range_up(host, start_port, end_port):
        port_range = f"{start_port}:{end_port}" if end_port else str(start_port)
        command = f"ssh {username}@{host} \"ufw status | grep '{port_range}.*ALLOW'\""

        result = subprocess.call(
            command,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return result == 0

    if end_port is None:
        end_port = start_port

    return server_range_up(host, start_port, end_port)


def is_ssh_server_reachable(server: dict) -> bool:
    command = f'ssh -q -o BatchMode=yes -o ConnectTimeout=5 {server["username"]}@{server["ip"]} "echo 2>&1"'
    ping = subprocess.call(command, shell=True)

    return ping == 0
