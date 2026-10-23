
import sqlite3
from pathlib import Path

DB_PATH = Path(r"C:\projects\intelli_assist_groq\data\intelli_assist.db")


def main():
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH, timeout=15)

    try:
        conn.execute("PRAGMA busy_timeout=15000")
        conn.execute("BEGIN IMMEDIATE")

        columns = {
            row[1]
            for row in conn.execute(
                "PRAGMA table_info(conversations)"
            ).fetchall()
        }

        required = {
            "session_id", "customer_id", "history_json",
            "updated_at", "summary", "facts_json"
        }

        missing = required - columns
        if missing:
            raise RuntimeError(f"Missing columns: {missing}")

        duplicates = conn.execute("""
            SELECT customer_id, session_id, COUNT(*)
            FROM conversations
            GROUP BY customer_id, session_id
            HAVING COUNT(*) > 1
        """).fetchall()

        if duplicates:
            raise RuntimeError(
                f"Duplicate customer/session pairs found: {duplicates[:10]}"
            )

        null_customers = conn.execute("""
            SELECT COUNT(*) FROM conversations
            WHERE customer_id IS NULL
        """).fetchone()[0]

        if null_customers:
            raise RuntimeError(
                f"{null_customers} rows have NULL customer_id. "
                "No changes committed."
            )

        conn.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS
            ux_conversations_customer_session
            ON conversations(customer_id, session_id)
        """)

        conn.commit()
        print("SUCCESS: Composite unique index created.")
        print("Existing conversation records preserved.")

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
