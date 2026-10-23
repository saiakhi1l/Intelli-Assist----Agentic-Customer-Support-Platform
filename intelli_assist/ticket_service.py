import secrets

from intelli_assist.storage import SQLiteStore


class TicketService:
    def __init__(self, store: SQLiteStore):
        self.store = store

    def create_ticket(
        self,
        customer_id: str,
        session_id: str,
        reason: str,
        description: str,
    ) -> str:
        ticket_id = (
            "IA-" + secrets.token_hex(4).upper()
        )

        self.store.create_ticket(
            ticket_id=ticket_id,
            customer_id=customer_id,
            session_id=session_id,
            reason=reason,
            description=description,
        )

        return ticket_id

    def get_customer_ticket(
        self,
        ticket_id: str,
        authenticated_customer_id: str,
    ):
        return self.store.get_ticket(
            ticket_id=ticket_id,
            customer_id=authenticated_customer_id,
        )