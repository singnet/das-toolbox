import base64
import getpass
import hashlib
import os
import secrets
import string
import sys
import time
from importlib import resources
from pathlib import Path
from typing import Callable, Optional

from common.logger import logger


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


def retry(func: Callable, max_retries=5, interval=2, *args, **kwargs):
    attempts = 0
    while attempts < max_retries:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            attempts += 1
            if attempts >= max_retries:
                raise e
            time.sleep(interval)


def deep_merge_dicts(dict1: dict, dict2: dict) -> dict:
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    return result


def resolve_file_path(
    relative_path: str,
    fallback_paths: list[str] = [],
) -> Optional[Path]:
    candidates: list[Path] = []

    candidates.extend(Path(p) for p in fallback_paths)

    if hasattr(sys, "_MEIPASS"):
        candidates.extend(Path(sys._MEIPASS) / p for p in fallback_paths)

    base_dir = Path(__file__).parent.resolve()
    candidates.extend(base_dir / p for p in fallback_paths)

    if hasattr(sys, "_MEIPASS"):
        candidates.append(Path(sys._MEIPASS) / relative_path)
    candidates.append(base_dir / relative_path)

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return None


def calculate_file_hash(file_path: Path) -> str:
    with open(file_path, "rb") as f:
        content = f.read()
    return hashlib.sha256(content).hexdigest()


def get_schema_hash() -> str:
    schema_path = resolve_file_path(
        "/etc/das-cli/schema.json",
        fallback_paths=[
            "settings/schema.json",
            "../settings/schema.json",
        ],
    )

    if schema_path is not None:
        return calculate_file_hash(schema_path)

    try:
        with resources.path("das_cli.settings", "schema.json") as pkg_path:
            return calculate_file_hash(pkg_path)
    except (FileNotFoundError, ModuleNotFoundError):
        pass

    raise FileNotFoundError("Schema file not found in any known location.")


def log_exception(e: Exception) -> None:
    error_type = e.__class__.__name__
    error_message = str(e)
    pretty_message = f"\033[31m[{error_type}] {error_message}\033[39m"

    logger().exception(error_message)

    print(pretty_message)
