"""
Builder for public_key_tokens parameter from atomdb configuration.

Extracts public keys from atomdb local database and remote peers,
constructing a tokenized string for authentication/authorization.
"""

from typing import Any


def _append_public_key_pair(
    tokens: list[str], database_config: dict[str, Any], config_path: str
) -> None:
    public_keys = database_config.get("public_keys")
    if public_keys is None or public_keys == []:
        return
    if not isinstance(public_keys, list):
        raise ValueError(f"{config_path}.public_keys must be an array.")

    uid = database_config.get("uid")
    public_key = public_keys[0]
    for field, value in (("uid", uid), ("public_keys[0]", public_key)):
        if not isinstance(value, str) or not value or any(character.isspace() for character in value):
            raise ValueError(f"{config_path}.{field} must be a single non-empty token.")

    tokens.append(f"{uid} {public_key}")


def build_public_key_tokens(atomdb_config: dict[str, Any]) -> str:
    """
    Build a space-separated public_key_tokens string from atomdb configuration.

    Format: "uid1 key1 uid2 key2 ... uidN keyN"
    - Iterates through local atomdb and all remote peers (including nested local_persistence)
    - For each, extracts uid and uses the first public_key from the public_keys array
    - Returns tokenized string suitable for Keychain.untokenize() on the server side

    Args:
        atomdb_config: The "atomdb" section from das.json containing uid, public_keys, and remote_peers

    Returns:
        Space-separated "uid1 key1 uid2 key2 ..." string, or empty string if no keys found

    Raises:
        ValueError: If public_keys is not an array or a UID/first key is not a single non-empty token
    """
    tokens: list[str] = []

    _append_public_key_pair(tokens, atomdb_config, "atomdb")

    for index, peer in enumerate(atomdb_config.get("remote_peers", [])):
        peer_path = f"atomdb.remote_peers[{index}]"
        _append_public_key_pair(tokens, peer, peer_path)

        local_persistence = peer.get("local_persistence")
        if local_persistence:
            _append_public_key_pair(tokens, local_persistence, f"{peer_path}.local_persistence")

    return " ".join(tokens)
