import sqlite3
from datetime import datetime, timezone

from shared.internal.constants import DATABASE_PATH
from shared.exceptions.custom_exceptions import SQLitePersistenceException


def save_service_metrics_data(machine_ip: str, service_data: dict[str, dict]) -> None:
    """Saves a metrics snapshot on the DB."""
    snapshot_time = datetime.now(timezone.utc).isoformat()
    rows = []

    for service_stats in service_data.values():
        if not isinstance(service_stats, dict):
            continue

        service_name = (
            service_stats.get("service_name")
            or service_stats.get("container_name")
            or service_stats.get("service_command_label")
        )
        if not service_name:
            continue

        cpu_usage = service_stats.get("cpu_percent")
        memory_usage = service_stats.get("memory_mb")
        rows.append(
            (
                machine_ip,
                str(service_name),
                str(cpu_usage if cpu_usage is not None else 0),
                str(memory_usage if memory_usage is not None else 0),
                snapshot_time,
            )
        )

    if not rows:
        return

    try:
        with sqlite3.connect(DATABASE_PATH) as connection:
            connection.executemany(
                """
                INSERT INTO service_metrics (
                    machine_ip, service_name, cpu_usage, memory_usage, timestamp
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                rows,
            )
    except (sqlite3.IntegrityError, sqlite3.OperationalError) as error:
        raise SQLitePersistenceException(str(error)) from error


def delete_metrics_by_ip(machine_ip: str) -> int:
    """Purges all stored metrics for a specific server."""
    try:
        with sqlite3.connect(DATABASE_PATH) as connection:
            cursor = connection.execute(
                "DELETE FROM service_metrics WHERE machine_ip = ?",
                (machine_ip,),
            )
            return cursor.rowcount
    except sqlite3.Error as error:
        raise SQLitePersistenceException(str(error)) from error


def delete_unused_metrics(keep_ips: list[str]) -> int:
    """Purges metrics whose machine_ip is no longer in the current architecture."""
    try:
        with sqlite3.connect(DATABASE_PATH) as connection:
            if not keep_ips:
                cursor = connection.execute("DELETE FROM service_metrics")
                return cursor.rowcount

            placeholders = ", ".join("?" for _ in keep_ips)
            cursor = connection.execute(
                f"DELETE FROM service_metrics WHERE machine_ip NOT IN ({placeholders})",
                keep_ips,
            )
            return cursor.rowcount
    except sqlite3.Error as error:
        raise SQLitePersistenceException(str(error)) from error


HISTORY_CHUNK_COUNT = 30
PERIOD_SECONDS = {
    "hour": 3600,
    "day": 86400,
    "week": 604800,
}


def get_service_metrics_averages(
    machine_ip: str,
    *,
    start: float,
    chunk_seconds: int,
    chunk_count: int = HISTORY_CHUNK_COUNT,
) -> list[tuple[str, int, float, float]]:
    """Averages CPU/memory per service into a fixed number of time chunks."""
    try:
        with sqlite3.connect(DATABASE_PATH) as connection:
            rows = connection.execute(
                """
                SELECT
                    service_name,
                    MIN(
                        ? - 1,
                        MAX(
                            0,
                            CAST(
                                (strftime('%s', substr(timestamp, 1, 19)) - ?) / ? AS INTEGER
                            )
                        )
                    ) AS bucket,
                    AVG(CAST(cpu_usage AS REAL)) AS avg_cpu,
                    AVG(CAST(memory_usage AS REAL)) AS avg_memory
                FROM service_metrics
                WHERE machine_ip = ?
                  AND strftime('%s', substr(timestamp, 1, 19)) >= ?
                GROUP BY service_name, bucket
                ORDER BY service_name, bucket
                """,
                (
                    chunk_count,
                    start,
                    chunk_seconds,
                    machine_ip,
                    start,
                ),
            ).fetchall()
    except sqlite3.Error as error:
        raise SQLitePersistenceException(str(error)) from error

    return [
        (service_name, int(bucket), float(avg_cpu or 0), float(avg_memory or 0))
        for service_name, bucket, avg_cpu, avg_memory in rows
    ]


def delete_all_metrics() -> int:
    """Purges metrics for every server."""
    try:
        with sqlite3.connect(DATABASE_PATH) as connection:
            cursor = connection.execute("DELETE FROM service_metrics")
            return cursor.rowcount
    except sqlite3.Error as error:
        raise SQLitePersistenceException(str(error)) from error
