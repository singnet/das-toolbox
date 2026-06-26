import os

from shared.internal.constants import ADAPTER_CONTEXT_MAPPING_FILE, CONFIG_DIR


def _ensure_config_dir() -> None:
    os.makedirs(CONFIG_DIR, exist_ok=True)


def save_context_mapping_content(content: str) -> dict:
    _ensure_config_dir()

    with open(ADAPTER_CONTEXT_MAPPING_FILE, "w", encoding="utf-8") as output:
        output.write(content or "")

    return {
        "message": "Context mapping saved successfully.",
        "saved_path": ADAPTER_CONTEXT_MAPPING_FILE,
    }


def validate_context_mapping_path(path: str) -> str:
    cleaned = (path or "").strip()
    if not cleaned:
        raise ValueError("Context mapping path is required.")

    if os.path.normpath(cleaned) == os.path.normpath(ADAPTER_CONTEXT_MAPPING_FILE):
        if not os.path.exists(cleaned):
            raise ValueError(
                "Context mapping file not found. Save the context mapping content first."
            )

    return cleaned
