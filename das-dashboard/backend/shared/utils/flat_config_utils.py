from copy import deepcopy

from shared.internal.configuration_constants import CONSTANTS, FLAT_SECTION_ORDER


def _merge_section(current_value, default_value):

    if isinstance(default_value, dict):
        current_dict = current_value if isinstance(current_value, dict) else {}
        merged = {}
        
        for key, default_item in default_value.items():
            current_item = current_dict.get(key)
            if current_item is not None:
                merged[key] = _merge_section(current_item, default_item)
            else:
                merged[key] = deepcopy(default_item)

        for key, current_item in current_dict.items():
            if key not in merged:
                merged[key] = deepcopy(current_item)
        return merged

    if current_value is not None:
        return deepcopy(current_value)

    return deepcopy(default_value)


def merge_flat_config(current: dict | None, defaults: dict | None = None) -> dict:
    """Fill missing flat sections and keys from *defaults* (saved config or CONSTANTS)."""
    current = current or {}
    defaults = defaults or CONSTANTS

    merged: dict = {}
    for key in FLAT_SECTION_ORDER:
        merged[key] = _merge_section(current.get(key), defaults[key])

    return merged
