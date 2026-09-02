import base64
import getpass
import os
import secrets
import string
import sys
import time
from pathlib import Path
from textwrap import shorten
from typing import Any, Callable, Dict, List, Optional

from common.logger import logger


def env_to_dict(path_to_env: Path):
    '''Opens an .env file and provide a dictionary with key/value pairs.'''
    content: dict = {}

    with open(path_to_env, "r") as env_file:

        for line in env_file:
            line.strip()

            if not line or line.startswith("#"):
                continue

            if "=" in line:
                key, value = line.split("=")
                content[key.strip()] = value.strip()

    return content


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


def search_dict_key(dict: dict[str, Any], path: str):
    keys = path.split(".")
    value: Any = dict

    for key in keys:
        value = value.get(key, None)
        if value is None:
            return None

    return value


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


def log_exception(e: Exception) -> None:
    error_type = e.__class__.__name__
    error_message = str(e)
    pretty_message = f"\033[31m[{error_type}] {error_message}\033[39m"

    logger().exception(error_message)

    print(pretty_message, file=sys.stderr)


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
        col: max(len(col), min(max_width, max(len(str(row.get(col, ""))) for row in rows)))
        for col in columns
    }

    if align is None:
        align = {col: "<" for col in columns}

    header = "  ".join(f"{col:{align.get(col, '<')}{col_widths[col]}}" for col in columns)
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


LOCAL_HOSTS = frozenset({"localhost", "127.0.0.1", "0.0.0.0"})
VAULT_ENDPOINT_HOSTS = frozenset({"localhost", "127.0.0.1"})


def extract_service_hostname(endpoint: str) -> str | None:
    try:
        hostname = endpoint.split(":")[0]
        return hostname
    except Exception:
        return None


def extract_service_port(endpoint: str) -> int | None:
    try:
        port = endpoint.split(":")[1]
        return int(port)
    except Exception:
        return None


def require_endpoint_port(
    endpoint: str | None,
    *,
    key: str = "endpoint",
    allowed_hosts: frozenset[str] | set[str] | None = None,
) -> tuple[str, int]:
    example = "localhost:40010"
    if not isinstance(endpoint, str) or not endpoint.strip():
        raise ValueError(
            f"Invalid or missing {key}. Expected host:port with an integer port, "
            f"for example '{example}'."
        )

    parts = endpoint.split(":")
    if len(parts) != 2:
        raise ValueError(
            f"Invalid {key} '{endpoint}'. Expected host:port with exactly one host and port, "
            f"for example '{example}'."
        )

    host, port_text = parts
    host = host.strip()
    if not host:
        raise ValueError(f"Invalid {key} '{endpoint}'. Hostname must not be empty.")

    if allowed_hosts is not None:
        allowed = {item.lower() for item in allowed_hosts}
        if host.lower() not in allowed:
            allowed_list = ", ".join(sorted(allowed_hosts))
            raise ValueError(
                f"Invalid {key} '{endpoint}'. Hostname must be one of: {allowed_list}."
            )

    try:
        port = int(port_text)
    except (TypeError, ValueError) as error:
        raise ValueError(
            f"Invalid {key} '{endpoint}'. Port must be an integer between 1 and 65535."
        ) from error

    if not (1 <= port <= 65535):
        raise ValueError(f"Invalid {key} port '{port}'. Port must be between 1 and 65535.")

    return host, port


def require_vault_endpoint(endpoint: str | None) -> tuple[str, int]:
    return require_endpoint_port(
        endpoint,
        key="vault.endpoint",
        allowed_hosts=VAULT_ENDPOINT_HOSTS,
    )


def get_platform_info() -> str:
    return f"{sys.platform} {sys.version.split()[0]}"
