"""
Builder for public_key_tokens parameter from atomdb configuration.

Extracts public keys from atomdb local database and remote peers,
constructing a tokenized string for authentication/authorization.
"""

from typing import Any


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
    """
    tokens: list[str] = []

    local_uid = atomdb_config.get("uid")
    local_public_keys = atomdb_config.get("public_keys", [])
    if local_uid and local_public_keys and len(local_public_keys) > 0:
        tokens.append(f"{local_uid} {local_public_keys[0]}")

    for peer in atomdb_config.get("remote_peers", []):
        peer_uid = peer.get("uid")
        peer_public_keys = peer.get("public_keys", [])
        if peer_uid and peer_public_keys and len(peer_public_keys) > 0:
            tokens.append(f"{peer_uid} {peer_public_keys[0]}")

        local_persistence = peer.get("local_persistence")
        if local_persistence:
            local_persist_uid = local_persistence.get("uid")
            local_persist_public_keys = local_persistence.get("public_keys", [])
            if local_persist_uid and local_persist_public_keys and len(local_persist_public_keys) > 0:
                tokens.append(f"{local_persist_uid} {local_persist_public_keys[0]}")

    return " ".join(tokens)
