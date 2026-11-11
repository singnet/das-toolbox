import pytest

from shared.exceptions.custom_exceptions import CustomValueError
from shared.utils.metta_load_validation import (
    atomdb_type_from_config,
    metta_load_supported,
    validate_atomdb_for_metta_load,
)


@pytest.mark.parametrize(
    "atomdb_type",
    ["redismongodb", "morkdb"],
)
def test_validate_allows_supported_types(atomdb_type):
    validate_atomdb_for_metta_load({"atomdb": {"type": atomdb_type}})


@pytest.mark.parametrize(
    "atomdb_type",
    ["inmemorydb", "remotedb", "adapterdb"],
)
def test_validate_rejects_unsupported_types(atomdb_type):
    with pytest.raises(CustomValueError):
        validate_atomdb_for_metta_load({"atomdb": {"type": atomdb_type}})


def test_validate_requires_atomdb_type():
    with pytest.raises(CustomValueError, match="atomdb.type"):
        validate_atomdb_for_metta_load({})


def test_atomdb_type_from_config():
    assert atomdb_type_from_config({"atomdb": {"type": "redismongodb"}}) == "redismongodb"
    assert atomdb_type_from_config({}) is None


def test_metta_load_supported():
    assert metta_load_supported("redismongodb")
    assert not metta_load_supported("remotedb")
