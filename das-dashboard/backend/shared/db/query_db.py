import json
import sqlite3
from datetime import datetime, timezone

from shared.internal.constants import QUERY_DB_PATH


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
