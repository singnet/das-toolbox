import re
import subprocess
from typing import Tuple, Union

import requests


def get_public_ip():
    try:
        return requests.get("https://api.ipify.org").content.decode("utf8")
    # TODO: better exception handler, for now do not use bare except
    except Exception:
        return None


# TODO: validate ip
def get_ssh_user_and_ip(text: str) -> Union[Tuple[str, str], None]:
    match = re.search(r"ssh:\/\/(\w+)@(\d{1,3}(?:\.\d{1,3}){3})(?::(\d+))?", text)

    if match:
        user = str(match.group(1))
        ip = str(match.group(2))

        return (user, ip)
    else:
        return None


def is_server_port_available(
    username: str,
    host: str,
    start_port: int,
    end_port: Union[int, None] = None,
):

    def server_port_up(host, start_port, end_port):

        node_port = end_port

        command = f"ssh {username}@{host} " f"'nc -z -w 5 localhost {node_port}'"

        # Using netcat instead of sudo ufw because it would break using any non root user.

        result = subprocess.call(
            command,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        return (
            False if result == 0 else True
        )  # nc return 0 if it connects to port, means its listening and not available.

    return server_port_up(host, start_port, end_port)


def is_ssh_server_reachable(server: dict) -> bool:
    command = f'ssh -q -o BatchMode=yes -o ConnectTimeout=5 {server["username"]}@{server["ip"]} "echo 2>&1"'
    ping = subprocess.call(command, shell=True)

    return ping == 0
