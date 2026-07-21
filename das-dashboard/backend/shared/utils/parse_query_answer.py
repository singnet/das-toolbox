import re
from typing import Any

# QueryAnswer<1,1> [[...]] {(V: "onivore")} (0.000000, 0.000000)
HEADER = re.compile(r"^QueryAnswer<\d+,\d+>\s+")
SCORES = re.compile(r" \(([-\d.]+),\s*([-\d.]+)\)\s*$")
ASSIGNMENT = re.compile(r"\{([^}]+)\}")
HANDLES = re.compile(r"\[\[(.*?)\]\]", re.DOTALL)
BINDING = re.compile(r"\(\s*([^:]+):\s*(.+)\s*\)")
COUNT_ONLY = re.compile(r"^\d+$")


def parse_query_answer(text: str) -> dict[str, Any]:
    if not isinstance(text, str) or not text.strip():
        return {"response": "", "importance": 0.0, "count_only": False}

    stripped = text.strip()

    if COUNT_ONLY.match(stripped):
        return {
            "response": stripped,
            "importance": 0.0,
            "count_only": True,
        }

    importance = 0.0
    body = text

    scores = SCORES.search(text)
    if scores:
        importance = float(scores.group(2))
        body = text[: scores.start()]

    response = stripped

    assignment = ASSIGNMENT.search(body)
    if assignment:
        binding = BINDING.search(assignment.group(1))
        if binding and binding.group(2).strip():
            response = binding.group(2).strip().strip('"')
            return {
                "response": response,
                "importance": importance,
                "count_only": False,
            }

    handles = HANDLES.search(body)
    if handles and handles.group(1).strip():
        response = handles.group(1).strip()

    return {
        "response": response,
        "importance": importance,
        "count_only": False,
    }


def transform_stream_event(event: dict[str, Any]) -> dict[str, Any]:
    if event.get("type") != "chunk":
        return event

    raw_items = event.get("data")
    if not isinstance(raw_items, list):
        return event

    data = []
    for item in raw_items:
        if isinstance(item, str):
            data.append(parse_query_answer(item))
            continue

        if isinstance(item, dict) and "response" in item:
            data.append(
                {
                    "response": item.get("response", ""),
                    "importance": float(item.get("importance", 0.0)),
                    "count_only": bool(item.get("count_only", False)),
                }
            )

    return {
        "execution_id": event.get("execution_id"),
        "type": "chunk",
        "seq": event.get("seq"),
        "received_count": event.get("received_count"),
        "data": data,
    }
