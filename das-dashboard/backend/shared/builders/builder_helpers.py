def _get(source, key, default=None):
    if source is None:
        return default
    if isinstance(source, dict):
        return source.get(key, default)
    return getattr(source, key, default)


def _is_missing(source, key) -> bool:
    if source is None:
        return True
    if isinstance(source, dict):
        if key not in source:
            return True
        return source[key] is None
    if not hasattr(source, key):
        return True
    return getattr(source, key) is None


def _require(source, *keys, label: str = "atomdb") -> None:
    missing = [key for key in keys if _is_missing(source, key)]
    if missing:
        raise ValueError(f"Missing required {label} fields: {missing}")
