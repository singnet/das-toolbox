import base64
import getpass
import hashlib
import os
import secrets
import string
import sys
import time
from pathlib import Path
from textwrap import shorten
from typing import Any, Callable, Dict, List, Optional

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


def calculate_schema_hash_for_keys(all_keys: List[str]) -> str:
    sorted_keys = sorted(all_keys)
    concatenated_keys = ",".join(sorted_keys)
    hash_object = hashlib.sha256(concatenated_keys.encode("utf-8"))
    return hash_object.hexdigest()


def calculate_schema_hash(schema: Dict[str, Any]) -> str:
    all_keys = list(schema.keys())

    return calculate_schema_hash_for_keys(all_keys)


def log_exception(e: Exception) -> None:
    error_type = e.__class__.__name__
    error_message = str(e)
    pretty_message = f"\033[31m[{error_type}] {error_message}\033[39m"

    logger().exception(error_message)

    print(pretty_message)


def print_table(
    rows: List[Dict[str, Any]],
    columns: List[str],
    align: Optional[Dict[str, str]] = None,
    max_width: int = 25,
    stdout=print,
) -> None:
    if not rows:
        stdout("No data to display.")
        return

    col_widths = {
        col: max(
            len(col), min(max_width, max(len(str(row.get(col, ""))) for row in rows))
        )
        for col in columns
    }

    if align is None:
        align = {col: "<" for col in columns}

    header = "  ".join(
        f"{col:{align.get(col, '<')}{col_widths[col]}}" for col in columns
    )
    stdout(header)
    stdout("-" * len(header))

    for row in rows:
        line = "  ".join(
            f"{shorten(str(row.get(col, '-')), width=col_widths[col], placeholder='…'):{align.get(col, '<')}{col_widths[col]}}"
            for col in columns
        )
        stdout(line)


def extract_service_name(container_name: str) -> str | None:
    if not isinstance(container_name, str):
        return None

    name = container_name
    if name.startswith("das-cli-"):
        name = name[len("das-cli-") :]

    parts = name.rsplit("-", 1)
    return parts[0] if parts else name
