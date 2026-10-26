import json
import os
from typing import Any
from urllib.parse import urlparse

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool


class PostgresStore:
    """Persistent PostgreSQL storage for IntelliAssist conversations and tickets."""

    def __init__(self, database_url: str | None = None):
        self.database_url = database_url or os.getenv("DATABASE_URL")

        if not self.database_url:
            raise RuntimeError(
                "DATABASE_URL is required for PostgreSQL storage."
            )

        # Normalize SQLAlchemy-style PostgreSQL URLs.
        self.database_url = self.database_url.replace(
            "postgresql+psycopg://",
            "postgresql://",
            1,
        )

        parsed = urlparse(self.database_url)

        if parsed.scheme not in ("postgres", "postgresql"):
            raise ValueError(
                "DATABASE_URL must be a PostgreSQL URL."
            )

        # Return query results as dictionaries.
        self.pool = ConnectionPool(
            conninfo=self.database_url,
            min_size=1,
            max_size=3,
            kwargs={
                "connect_timeout": 10,
                "row_factory": dict_row,
            },
            open=False,
            check=ConnectionPool.check_connection,
            max_lifetime=300,
            max_idle=60,
        )

        self.pool.open(wait=True)
        self._initialize()

    def _initialize(self) -> None:
        """Create database tables if they do not already exist."""
        with self.pool.connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    customer_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    history_json TEXT NOT NULL DEFAULT '[]',
                    summary TEXT NOT NULL DEFAULT '',
                    facts_json TEXT NOT NULL DEFAULT '[]',
                    updated_at TIMESTAMPTZ NOT NULL
                        DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (customer_id, session_id)
                )
                """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tickets (
                    ticket_id TEXT PRIMARY KEY,
                    subject TEXT NOT NULL
                        DEFAULT 'Customer support request',
                    description TEXT NOT NULL DEFAULT '',
                    customer_id TEXT NOT NULL,
                    priority TEXT NOT NULL DEFAULT 'medium',
                    status TEXT NOT NULL DEFAULT 'open',
                    created_at TIMESTAMPTZ NOT NULL
                        DEFAULT CURRENT_TIMESTAMP,
                    session_id TEXT NOT NULL DEFAULT '',
                    reason TEXT NOT NULL DEFAULT ''
                )
                """
            )

    def get_conversation(
        self,
        customer_id: str,
        session_id: str,
    ) -> dict[str, Any]:
        """Retrieve conversation history, summary, and stored facts."""
        with self.pool.connection() as conn:
            row = conn.execute(
                """
                SELECT history_json, summary, facts_json
                FROM conversations
                WHERE customer_id = %s
                  AND session_id = %s
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
        """Insert or update a conversation."""
        with self.pool.connection() as conn:
            conn.execute(
                """
                INSERT INTO conversations (
                    customer_id,
                    session_id,
                    history_json,
                    summary,
                    facts_json
                )
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (customer_id, session_id)
                DO UPDATE SET
                    history_json = EXCLUDED.history_json,
                    summary = EXCLUDED.summary,
                    facts_json = EXCLUDED.facts_json,
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
        priority: str = "medium",
    ) -> None:
        """Create a support ticket with its assigned priority."""

        # Normalize and validate the priority before inserting.
        normalized_priority = (priority or "medium").strip().lower()

        allowed_priorities = {
            "low",
            "medium",
            "high",
            "urgent",
        }

        if normalized_priority not in allowed_priorities:
            normalized_priority = "medium"

        normalized_reason = (reason or "").strip()

        subject = (
            normalized_reason
            if normalized_reason
            else "Customer support request"
        )

        with self.pool.connection() as conn:
            conn.execute(
                """
                INSERT INTO tickets (
                    ticket_id,
                    subject,
                    description,
                    customer_id,
                    priority,
                    status,
                    session_id,
                    reason
                )
                VALUES (%s, %s, %s, %s, %s, 'open', %s, %s)
                """,
                (
                    ticket_id,
                    subject,
                    description or "",
                    customer_id,
                    normalized_priority,
                    session_id or "",
                    normalized_reason or subject,
                ),
            )

    def get_ticket(
        self,
        ticket_id: str,
        customer_id: str,
    ) -> dict[str, Any] | None:
        """Retrieve a ticket belonging to the specified customer."""
        with self.pool.connection() as conn:
            row = conn.execute(
                """
                SELECT
                    ticket_id,
                    subject,
                    description,
                    customer_id,
                    priority,
                    status,
                    created_at,
                    session_id,
                    reason
                FROM tickets
                WHERE ticket_id = %s
                  AND customer_id = %s
                """,
                (ticket_id, customer_id),
            ).fetchone()

        if row is None:
            return None

        result = dict(row)

        if result.get("created_at") is not None:
            result["created_at"] = result["created_at"].isoformat()

        return result

    def close(self) -> None:
        """Close the PostgreSQL connection pool."""
        self.pool.close()
