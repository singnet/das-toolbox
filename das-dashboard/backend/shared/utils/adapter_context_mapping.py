import os

from shared.internal.constants import ADAPTER_CONTEXT_MAPPING_FILE, CONFIG_DIR

PATH_FILE = os.path.join(CONFIG_DIR, "adapter_context_mapping.path")


def _ensure_config_dir() -> None:
    os.makedirs(CONFIG_DIR, exist_ok=True)


def _read_saved_path() -> str:
    if os.path.exists(PATH_FILE):
        with open(PATH_FILE, "r", encoding="utf-8") as source:
            saved_path = source.read().strip()
            if saved_path:
                return saved_path

    return ADAPTER_CONTEXT_MAPPING_FILE


def _write_saved_path(path: str) -> None:
    _ensure_config_dir()

    with open(PATH_FILE, "w", encoding="utf-8") as output:
        output.write(path)


def save_context_mapping_content(content: str) -> dict:
    _ensure_config_dir()

    with open(ADAPTER_CONTEXT_MAPPING_FILE, "w", encoding="utf-8") as output:
        output.write(content or "")

    _write_saved_path(ADAPTER_CONTEXT_MAPPING_FILE)

    return {
        "message": "Context mapping saved successfully.",
        "saved_path": ADAPTER_CONTEXT_MAPPING_FILE,
    }


def save_context_mapping_path(path: str) -> dict:
    cleaned_path = (path or "").strip()
    if not cleaned_path:
        raise ValueError("Context mapping path is required.")

    _write_saved_path(cleaned_path)

    return {
        "message": "Context mapping path saved successfully.",
        "saved_path": cleaned_path,
    }


def resolve_context_mapping_path() -> str:
    return _read_saved_path()


def sync_context_mapping_from_nested(nested_config: dict) -> None:
    atomdb = nested_config.get("atomdb", {})
    if atomdb.get("type") != "adapterdb":
        return

    paths = atomdb.get("adapterdb", {}).get("context_mapping_paths") or []
    if paths:
        _write_saved_path(paths[0])
