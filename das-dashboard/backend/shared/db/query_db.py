import json
import sqlite3
from datetime import datetime, timezone

from shared.internal.constants import QUERY_DB_PATH


def _next_answer_index(connection: sqlite3.Connection, execution_id: str) -> int:
    cursor = connection.execute(
        "SELECT COALESCE(MAX(answer_index), -1) FROM query_answers WHERE execution_id = ?",
        (execution_id,),
    )
    return cursor.fetchone()[0] + 1


def save_event(execution_id: str, payload: dict) -> None:
    created_at = datetime.now(timezone.utc).isoformat()

    with sqlite3.connect(QUERY_DB_PATH) as connection:
        connection.execute(
            """
            INSERT INTO query_events (
                execution_id, event_type, status, seq, received_count, payload_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                execution_id,
                payload.get("type"),
                payload.get("status"),
                payload.get("seq"),
                payload.get("received_count"),
                json.dumps(payload),
                created_at,
            ),
        )
        connection.commit()


def save_answers_from_chunk(execution_id: str, payload: dict) -> None:
    data = payload.get("data")
    if not isinstance(data, list) or not data:
        return

    seq = payload.get("seq")
    created_at = datetime.now(timezone.utc).isoformat()

    with sqlite3.connect(QUERY_DB_PATH) as connection:
        next_index = _next_answer_index(connection, execution_id)
        rows = []

        for item in data:
            if not isinstance(item, dict):
                continue

            rows.append(
                (
                    execution_id,
                    seq,
                    next_index,
                    str(item.get("response", "")),
                    0.0,
                    float(item.get("importance", 0.0)),
                    None,
                    created_at,
                )
            )
            next_index += 1

        if not rows:
            return

        connection.executemany(
            """
            INSERT INTO query_answers (
                execution_id, seq, answer_index, answer_text, strength, importance,
                assignment_label, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        connection.commit()


def get_answers_page(
    execution_id: str,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    page = max(1, page)
    page_size = min(max(1, page_size), 100)
    offset = (page - 1) * page_size

    with sqlite3.connect(QUERY_DB_PATH) as connection:
        total = connection.execute(
            "SELECT COUNT(*) FROM query_answers WHERE execution_id = ?",
            (execution_id,),
        ).fetchone()[0]

        rows = connection.execute(
            """
            SELECT answer_index, answer_text, importance
            FROM query_answers
            WHERE execution_id = ?
            ORDER BY answer_index ASC
            LIMIT ? OFFSET ?
            """,
            (execution_id, page_size, offset),
        ).fetchall()

    total_pages = (total + page_size - 1) // page_size if total else 0

    return {
        "execution_id": execution_id,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
        "items": [
            {
                "id": row[0],
                "response": row[1],
                "importance": row[2],
            }
            for row in rows
        ],
    }
