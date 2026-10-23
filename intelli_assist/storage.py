
import json
import sqlite3
from pathlib import Path
from threading import RLock
from typing import Any


class SQLiteStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()
        self._initialize()

    def _connect(self):
        connection = sqlite3.connect(
            self.db_path,
            timeout=15,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout=15000")
        connection.execute("PRAGMA foreign_keys=ON")
        return connection

    def _initialize(self):
        with self._lock, self._connect() as conn:
            conn.execute("PRAGMA journal_mode=WAL")

            # Create conversations table for new databases.
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    customer_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    history_json TEXT NOT NULL DEFAULT '[]',
                    summary TEXT NOT NULL DEFAULT '',
                    facts_json TEXT NOT NULL DEFAULT '[]',
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (customer_id, session_id)
                )
            """)

            conversation_columns = {
                row["name"]
                for row in conn.execute(
                    "PRAGMA table_info(conversations)"
                ).fetchall()
            }

            # Migrate older conversation tables without deleting data.
            conversation_migrations = {
                "customer_id": (
                    "ALTER TABLE conversations "
                    "ADD COLUMN customer_id TEXT"
                ),
                "session_id": (
                    "ALTER TABLE conversations "
                    "ADD COLUMN session_id TEXT"
                ),
                "history_json": (
                    "ALTER TABLE conversations "
                    "ADD COLUMN history_json TEXT NOT NULL DEFAULT '[]'"
                ),
                "summary": (
                    "ALTER TABLE conversations "
                    "ADD COLUMN summary TEXT NOT NULL DEFAULT ''"
                ),
                "facts_json": (
                    "ALTER TABLE conversations "
                    "ADD COLUMN facts_json TEXT NOT NULL DEFAULT '[]'"
                ),
                "updated_at": (
                    "ALTER TABLE conversations "
                    "ADD COLUMN updated_at TEXT NOT NULL DEFAULT ''"
                ),
            }

            for column_name, sql in conversation_migrations.items():
                if column_name not in conversation_columns:
                    conn.execute(sql)

            conn.execute("""
                UPDATE conversations
                SET updated_at = CURRENT_TIMESTAMP
                WHERE updated_at IS NULL OR updated_at = ''
            """)

            # Verify conversation keys before creating the unique index.
            null_pair = conn.execute("""
                SELECT COUNT(*) AS row_count
                FROM conversations
                WHERE customer_id IS NULL OR session_id IS NULL
            """).fetchone()["row_count"]

            if null_pair:
                raise RuntimeError(
                    f"{null_pair} conversation rows have a NULL "
                    "customer_id or session_id. Resolve these records "
                    "before continuing."
                )

            duplicates = conn.execute("""
                SELECT customer_id, session_id, COUNT(*) AS row_count
                FROM conversations
                GROUP BY customer_id, session_id
                HAVING COUNT(*) > 1
                LIMIT 1
            """).fetchone()

            if duplicates:
                raise RuntimeError(
                    "Duplicate customer/session pair found: "
                    f"{duplicates['customer_id']!r}, "
                    f"{duplicates['session_id']!r}. "
                    "Resolve duplicates before continuing."
                )

            conn.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS
                ux_conversations_customer_session
                ON conversations(customer_id, session_id)
            """)

            # Create tickets table for new databases.
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tickets (
                    ticket_id TEXT PRIMARY KEY,
                    subject TEXT NOT NULL DEFAULT 'Customer support request',
                    description TEXT NOT NULL DEFAULT '',
                    customer_id TEXT NOT NULL,
                    priority TEXT NOT NULL DEFAULT 'medium',
                    status TEXT NOT NULL DEFAULT 'open',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    session_id TEXT NOT NULL DEFAULT '',
                    reason TEXT NOT NULL DEFAULT ''
                )
            """)

            ticket_columns = {
                row["name"]
                for row in conn.execute(
                    "PRAGMA table_info(tickets)"
                ).fetchall()
            }

            # Add missing columns while retaining the old ticket schema.
            ticket_migrations = {
                "subject": (
                    "ALTER TABLE tickets ADD COLUMN "
                    "subject TEXT NOT NULL DEFAULT 'Customer support request'"
                ),
                "description": (
                    "ALTER TABLE tickets ADD COLUMN "
                    "description TEXT NOT NULL DEFAULT ''"
                ),
                "customer_id": (
                    "ALTER TABLE tickets ADD COLUMN customer_id TEXT"
                ),
                "priority": (
                    "ALTER TABLE tickets ADD COLUMN "
                    "priority TEXT NOT NULL DEFAULT 'medium'"
                ),
                "status": (
                    "ALTER TABLE tickets ADD COLUMN "
                    "status TEXT NOT NULL DEFAULT 'open'"
                ),
                "created_at": (
                    "ALTER TABLE tickets ADD COLUMN "
                    "created_at TEXT NOT NULL DEFAULT ''"
                ),
                "session_id": (
                    "ALTER TABLE tickets ADD COLUMN "
                    "session_id TEXT NOT NULL DEFAULT ''"
                ),
                "reason": (
                    "ALTER TABLE tickets ADD COLUMN "
                    "reason TEXT NOT NULL DEFAULT ''"
                ),
            }

            for column_name, sql in ticket_migrations.items():
                if column_name not in ticket_columns:
                    conn.execute(sql)

            # Backfill existing records.
            conn.execute("""
                UPDATE tickets
                SET created_at = CURRENT_TIMESTAMP
                WHERE created_at IS NULL OR created_at = ''
            """)

            conn.execute("""
                UPDATE tickets
                SET subject = 'Customer support request'
                WHERE subject IS NULL OR subject = ''
            """)

            conn.execute("""
                UPDATE tickets
                SET priority = 'medium'
                WHERE priority IS NULL OR priority = ''
            """)

            conn.execute("""
                UPDATE tickets
                SET status = 'open'
                WHERE status IS NULL OR status = ''
            """)

            conn.execute("""
                UPDATE tickets
                SET description = ''
                WHERE description IS NULL
            """)

            conn.execute("""
                UPDATE tickets
                SET reason = subject
                WHERE reason IS NULL OR reason = ''
            """)

    def get_conversation(
        self,
        customer_id: str,
        session_id: str,
    ) -> dict[str, Any]:
        with self._lock, self._connect() as conn:
            row = conn.execute(
                """
                SELECT history_json, summary, facts_json
                FROM conversations
                WHERE customer_id = ? AND session_id = ?
                """,
                (customer_id, session_id),
            ).fetchone()

        if row is None:
            return {
                "history": [],
                "summary": "",
                "facts": [],
            }

        return {
            "history": json.loads(row["history_json"] or "[]"),
            "summary": row["summary"] or "",
            "facts": json.loads(row["facts_json"] or "[]"),
        }

    def save_conversation(
        self,
        customer_id: str,
        session_id: str,
        history: list[dict[str, str]],
        summary: str = "",
        facts: list[dict[str, Any]] | None = None,
    ) -> None:
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                INSERT INTO conversations (
                    customer_id,
                    session_id,
                    history_json,
                    summary,
                    facts_json,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(customer_id, session_id)
                DO UPDATE SET
                    history_json = excluded.history_json,
                    summary = excluded.summary,
                    facts_json = excluded.facts_json,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    customer_id,
                    session_id,
                    json.dumps(history, ensure_ascii=False),
                    summary,
                    json.dumps(facts or [], ensure_ascii=False),
                ),
            )

    def create_ticket(
        self,
        ticket_id: str,
        customer_id: str,
        session_id: str,
        reason: str,
        description: str,
    ) -> None:
        subject = reason.strip() if reason and reason.strip() else (
            "Customer support request"
        )

        with self._lock, self._connect() as conn:
            conn.execute(
                """
                INSERT INTO tickets (
                    ticket_id,
                    subject,
                    description,
                    customer_id,
                    priority,
                    status,
                    created_at,
                    session_id,
                    reason
                )
                VALUES (
                    ?, ?, ?, ?, 'medium', 'open',
                    CURRENT_TIMESTAMP, ?, ?
                )
                """,
                (
                    ticket_id,
                    subject,
                    description or "",
                    customer_id,
                    session_id or "",
                    reason or subject,
                ),
            )

    def get_ticket(
        self,
        ticket_id: str,
        customer_id: str,
    ) -> dict[str, Any] | None:
        with self._lock, self._connect() as conn:
            row = conn.execute(
                """
                SELECT ticket_id, subject, description, customer_id,
                       priority, status, created_at, session_id, reason
                FROM tickets
                WHERE ticket_id = ? AND customer_id = ?
                """,
                (ticket_id, customer_id),
            ).fetchone()

        return dict(row) if row else None
