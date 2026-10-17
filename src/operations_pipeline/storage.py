"""Idempotent SQLite persistence and aggregate reporting."""
import csv
import sqlite3
from pathlib import Path
from .validation import Transaction

SCHEMA = """CREATE TABLE IF NOT EXISTS transactions (
    transaction_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    transaction_date TEXT NOT NULL,
    category TEXT NOT NULL,
    amount_cents INTEGER NOT NULL CHECK (amount_cents >= 0),
    status TEXT NOT NULL
)"""


def connect(db_path: str | Path) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.execute(SCHEMA)
    connection.commit()
    return connection


def save(connection: sqlite3.Connection, records: list[Transaction]) -> int:
    before = connection.total_changes
    with connection:
        connection.executemany("""INSERT OR IGNORE INTO transactions
            (transaction_id, customer_id, transaction_date, category, amount_cents, status)
            VALUES (?, ?, ?, ?, ?, ?)""", [
                (r.transaction_id, r.customer_id, r.date, r.category, r.amount_cents, r.status)
                for r in records
            ])
    return connection.total_changes - before


def export_summary(connection: sqlite3.Connection, destination: str | Path) -> Path:
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = connection.execute("""SELECT category, status, COUNT(*) AS transactions,
        SUM(amount_cents) AS total_cents
        FROM transactions GROUP BY category, status ORDER BY category, status""").fetchall()
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(("category", "status", "transaction_count", "total_amount"))
        for category, status, count, cents in rows:
            writer.writerow((category, status, count, f"{cents // 100}.{cents % 100:02d}"))
    return path
