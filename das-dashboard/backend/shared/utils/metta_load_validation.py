from shared.exceptions.custom_exceptions import CustomValueError

METTA_LOAD_ALLOWED_TYPES = frozenset({"redismongodb", "morkdb"})

_BLOCKED_MESSAGES = {
    "inmemorydb": (
        "MeTTa load is not supported for In-Memory AtomDB. "
        "There is no persistent database to load into."
    ),
    "remotedb": (
        "MeTTa load is disabled for RemoteDB in the dashboard for now. "
        "Per-peer loading (sub-config Redis + MongoDB or Mork + MongoDB) "
        "will be supported in a follow-up."
    ),
    "adapterdb": (
        "MeTTa load is not supported for AdapterDB. "
        "Use Redis + MongoDB or Mork + MongoDB for loading MeTTa files."
    ),
}


def atomdb_type_from_config(config: dict) -> str | None:
    atomdb = config.get("atomdb")
    if not isinstance(atomdb, dict):
        return None
    atomdb_type = atomdb.get("type")
    if not isinstance(atomdb_type, str) or not atomdb_type.strip():
        return None
    return atomdb_type.strip()


def validate_atomdb_for_metta_load(config: dict) -> None:
    atomdb_type = atomdb_type_from_config(config)
    if not atomdb_type:
        raise CustomValueError(
            "MeTTa load requires a saved configuration with atomdb.type set."
        )

    if atomdb_type in METTA_LOAD_ALLOWED_TYPES:
        return

    message = _BLOCKED_MESSAGES.get(
        atomdb_type,
        f"MeTTa load is not supported for AtomDB type '{atomdb_type}'. "
        f"Supported types: {', '.join(sorted(METTA_LOAD_ALLOWED_TYPES))}.",
    )
    raise CustomValueError(message)


def metta_load_supported(atomdb_type: str | None) -> bool:
    return atomdb_type in METTA_LOAD_ALLOWED_TYPES
