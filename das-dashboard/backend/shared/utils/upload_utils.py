import os

def safe_upload_filename(filename: str | None) -> str:
    if not filename:
        raise ValueError("Invalid upload filename.")

    name = filename.strip()
    if not name or name in {".", ".."}:
        raise ValueError("Invalid upload filename.")

    if name != os.path.basename(name) or "/" in name or "\\" in name:
        raise ValueError("Invalid upload filename.")

    return name
