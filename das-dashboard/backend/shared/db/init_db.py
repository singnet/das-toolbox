import os
import sqlite3

from shared.internal.constants import QUERY_DB_PATH

QUERY_EVENT_SCHEMA = """
CREATE TABLE IF NOT EXISTS query_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id TEXT NOT NULL,
    event_type TEXT,
    status TEXT,
    seq INTEGER,
    received_count INTEGER,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_query_events_execution_id
    ON query_events(execution_id);
"""

QUERY_ANSWER_SCHEMA = """
CREATE TABLE IF NOT EXISTS query_answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id TEXT NOT NULL,
    seq INTEGER,
    answer_index INTEGER NOT NULL,
    answer_text TEXT NOT NULL,
    strength REAL NOT NULL,
    importance REAL NOT NULL,
    assignment_label TEXT,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_query_answers_execution_id
    ON query_answers(execution_id);
"""

SCHEMAS = (
    QUERY_EVENT_SCHEMA,
    QUERY_ANSWER_SCHEMA,
)


def init_db() -> None:
    os.makedirs(os.path.dirname(QUERY_DB_PATH), exist_ok=True)

    with sqlite3.connect(QUERY_DB_PATH) as connection:
        for schema in SCHEMAS:
            connection.executescript(schema)
