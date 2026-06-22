from shared.internal.configuration_constants import CONSTANTS, FLAT_SECTION_ORDER


def merge_flat_config(current: dict | None, defaults: dict | None = None) -> dict:
    """Fill missing flat sections from *default* (saved config or CONSTANTS)."""
    current = current or {}
    defaults = defaults or CONSTANTS

    merged: dict = {}
    for key in FLAT_SECTION_ORDER:
        section = current.get(key)
        if section:
            merged[key] = section
        else:
            merged[key] = defaults[key]

    return merged
