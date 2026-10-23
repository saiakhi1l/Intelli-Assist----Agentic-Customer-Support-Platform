import uuid

class TicketRepository:
    def __init__(self, settings):
        self.settings, self.local, self.pool = settings, {}, None
        if settings.database_enabled:
            from psycopg_pool import ConnectionPool
            self.pool = ConnectionPool(settings.database_url, min_size=1, max_size=5, open=True)
            with self.pool.connection() as conn:
                conn.execute("CREATE TABLE IF NOT EXISTS tickets (ticket_id TEXT PRIMARY KEY, subject TEXT NOT NULL, description TEXT NOT NULL, customer_id TEXT, priority TEXT NOT NULL, status TEXT NOT NULL)")
                conn.commit()

    def create(self, subject, description, customer_id=None, priority="normal"):
        tid = "TKT-" + uuid.uuid4().hex[:10].upper()
        item = dict(ticket_id=tid, subject=subject, description=description,
                    customer_id=customer_id, priority=priority, status="open")
        if self.pool:
            with self.pool.connection() as conn:
                conn.execute("INSERT INTO tickets (ticket_id,subject,description,customer_id,priority,status) VALUES (%s,%s,%s,%s,%s,%s)",
                             (tid, subject, description, customer_id, priority, "open"))
                conn.commit()
        else:
            self.local[tid] = item
        return item

    def get(self, ticket_id):
        if self.pool:
            with self.pool.connection() as conn:
                row = conn.execute("SELECT ticket_id,subject,description,customer_id,priority,status FROM tickets WHERE ticket_id=%s", (ticket_id,)).fetchone()
                if not row: return None
                return dict(zip(["ticket_id","subject","description","customer_id","priority","status"], row))
        return self.local.get(ticket_id)
