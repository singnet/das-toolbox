from shared.exceptions.custom_exceptions import CustomValueError

METTA_LOAD_ALLOWED_TYPES = frozenset({"redismongodb", "morkdb"})

_UNSUPPORTED_MESSAGE = (
    "MeTTa load is disabled for this AtomDB type. "
    "Only Redis + MongoDB and Mork + MongoDB can be loaded for now."
)


def validate_atomdb_for_metta_load(config: dict) -> None:
    atomdb = config.get("atomdb") if isinstance(config, dict) else None
    atomdb_type = atomdb.get("type") if isinstance(atomdb, dict) else None
    if not isinstance(atomdb_type, str) or not atomdb_type.strip():
        raise CustomValueError(
            "MeTTa load requires a saved configuration with atomdb.type set."
        )

    if atomdb_type.strip() not in METTA_LOAD_ALLOWED_TYPES:
        raise CustomValueError(_UNSUPPORTED_MESSAGE)
