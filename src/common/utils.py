import os
import sys
import getpass
import subprocess


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


def generate_keyfile(path: str):
    keyfile_content = subprocess.check_output(["openssl", "rand", "-base64", "756"])

    with open(path, "wb") as keyfile:
        keyfile.write(keyfile_content)

    os.chmod(path, 0o400)
