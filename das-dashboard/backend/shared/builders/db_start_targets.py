from shared.internal.constants import LOCAL_HOSTS
from shared.utils.path_utils import split_endpoint

STARTABLE_LOCAL_PERSISTENCE = frozenset({"redismongodb", "morkdb"})


def build_db_start_targets(atomdb: dict, profile_username: str = "") -> list[dict]:
    """SSH hints for RemoteDB local persistence.

    The CLI will read this list, create Docker contexts, for remote initialization.
    """
    if not isinstance(atomdb, dict) or atomdb.get("type") != "remotedb":
        return []

    targets = []
    for peer in atomdb.get("remote_peers") or []:
        if not isinstance(peer, dict):
            continue
        local_persistence = peer.get("local_persistence") or {}
        if not isinstance(local_persistence, dict):
            continue
        persistence_type = local_persistence.get("type")
        if persistence_type not in STARTABLE_LOCAL_PERSISTENCE:
            continue

        host = _persistence_host(local_persistence, persistence_type)
        local = not host or host in LOCAL_HOSTS
        targets.append({
            "codename": local_persistence.get("context") or f"{peer.get('uid') or 'peer'}-local",
            "type": persistence_type,
            "nodes": [{
                "context": "default" if local else "",
                "ip": "localhost" if local else host,
                "username": profile_username or "",
            }],
        })
    return targets


def _persistence_host(local_persistence: dict, persistence_type: str) -> str:
    if persistence_type == "redismongodb":
        endpoint = (local_persistence.get("redis") or {}).get("endpoint")
        if not endpoint:
            endpoint = (local_persistence.get("mongodb") or {}).get("endpoint")
    else:
        endpoint = (local_persistence.get("morkdb") or {}).get("endpoint")
        if not endpoint:
            endpoint = (local_persistence.get("mongodb") or {}).get("endpoint")

    if not isinstance(endpoint, str) or not endpoint:
        return ""
    host, _ = split_endpoint(endpoint, "", 0)
    return host
