from typing import Any


def _to_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def normalize_query_answer(item: Any) -> dict[str, Any] | None:
    if isinstance(item, str) and item.strip().isdigit():
        return {"count_only": True, "count": int(item.strip())}

    if not isinstance(item, dict):
        return None

    if "handles" not in item or "assignment" not in item:
        return None

    metta_expressions = item.get("metta_expressions")
    if metta_expressions is None:
        metta_expressions = item.get("metta", [])

    normalized = dict(item)
    normalized.update(
        {
            "handles": item.get("handles", []),
            "assignment": item.get("assignment", {}),
            "metta_expressions": metta_expressions or [],
            "assignment_metta": item.get("assignment_metta", {}),
            "importance": _to_float(item.get("importance")),
            "strength": _to_float(item.get("strength")),
        }
    )
    return normalized


def transform_stream_event(event: dict[str, Any]) -> dict[str, Any]:
    if event.get("type") != "chunk":
        return event

    raw_items = event.get("data")
    if not isinstance(raw_items, list):
        return event

    data = []
    for item in raw_items:
        normalized = normalize_query_answer(item)
        if normalized is not None:
            data.append(normalized)

    return {
        "execution_id": event.get("execution_id"),
        "type": "chunk",
        "seq": event.get("seq"),
        "received_count": event.get("received_count"),
        "data": data,
    }
