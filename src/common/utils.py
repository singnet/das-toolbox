import base64
import getpass
import os
import secrets
import string
import sys
import time


def is_executable_bin():
    return getattr(sys, "frozen", False)


def get_script_name():
    if is_executable_bin():
        return os.path.basename(sys.executable)
    else:
        return "python3 " + sys.argv[0]


def get_server_username() -> str:
    return getpass.getuser()


def remove_special_characters(text):
    import re

    pattern = r"[^a-zA-Z0-9\s]"

    clean_text = re.sub(pattern, "", text)

    return clean_text.strip()


def get_rand_token(num_bytes: int = 756, only_alpha: bool = True) -> str:
    if only_alpha:
        alphabet = string.ascii_letters + string.digits
        token = "".join(secrets.choice(alphabet) for _ in range(num_bytes))
        return token

    random_bytes = secrets.token_bytes(num_bytes)

    return base64.b64encode(random_bytes).decode("utf-8")


def retry(func: callable, max_retries=5, interval=2, *args, **kwargs):
    attempts = 0
    while attempts < max_retries:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            attempts += 1
            if attempts >= max_retries:
                raise e
            time.sleep(interval)
