"""RemoteDB local persistences that `db start` should run.

Nodes come from ``db_start_targets``. Endpoints stay on the peer's
``local_persistence``. Each node keeps the container-manager shape:
context, ip, username.
"""

STARTABLE_TYPES = frozenset({"redismongodb", "morkdb"})


def remote_local_persistences(config: dict) -> list[dict]:
    atomdb = config.get("atomdb") or {}
    if not isinstance(atomdb, dict) or atomdb.get("type") != "remotedb":
        return []

    peers_by_codename = _peers_by_codename(atomdb.get("remote_peers") or [])
    persistences = []
    for target in config.get("db_start_targets") or []:
        if not isinstance(target, dict):
            continue
        peer = peers_by_codename.get(target.get("codename") or "")
        if not peer:
            continue
        local_persistence = peer.get("local_persistence") or {}
        persistence_type = target.get("type") or local_persistence.get("type")
        if persistence_type not in STARTABLE_TYPES:
            continue
        persistence = _persistence_with_nodes(peer, persistence_type, _nodes_from_target(target))
        if persistence:
            persistences.append(persistence)
    return persistences


def _peers_by_codename(peers: list) -> dict[str, dict]:
    indexed = {}
    for peer in peers:
        if not isinstance(peer, dict):
            continue
        local_persistence = peer.get("local_persistence") or {}
        if not isinstance(local_persistence, dict):
            continue
        codename = local_persistence.get("context") or ""
        if codename:
            indexed[codename] = peer
    return indexed


def _nodes_from_target(target: dict) -> list[dict]:
    nodes = target.get("nodes")
    if isinstance(nodes, list) and nodes:
        return [dict(node) for node in nodes if isinstance(node, dict)]
    return [
        {
            "context": target.get("context") or "",
            "ip": target.get("ip") or "localhost",
            "username": target.get("username") or "",
        }
    ]


def _persistence_with_nodes(peer: dict, persistence_type: str, nodes: list[dict]) -> dict | None:
    local_persistence = peer.get("local_persistence") or {}
    persistence = {
        "codename": local_persistence.get("context") or peer.get("uid") or "",
        "type": persistence_type,
        "nodes": nodes,
    }
    if persistence_type == "redismongodb":
        redis = dict(local_persistence.get("redis") or {})
        mongodb = dict(local_persistence.get("mongodb") or {})
        if not redis.get("endpoint") or not mongodb.get("endpoint"):
            return None
        redis["nodes"] = nodes
        mongodb["nodes"] = nodes
        persistence["redis"] = redis
        persistence["mongodb"] = mongodb
        return persistence

    if persistence_type == "morkdb":
        morkdb = dict(local_persistence.get("morkdb") or {})
        mongodb = dict(local_persistence.get("mongodb") or {})
        if not morkdb.get("endpoint") or not mongodb.get("endpoint"):
            return None
        morkdb["nodes"] = nodes
        mongodb["nodes"] = nodes
        persistence["morkdb"] = morkdb
        persistence["mongodb"] = mongodb
        return persistence

    return None
