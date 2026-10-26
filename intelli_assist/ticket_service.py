
import secrets


class TicketService:
    """Business logic for creating and retrieving support tickets."""

    def __init__(self, store):
        self.store = store

    def create_ticket(
        self,
        customer_id: str,
        session_id: str,
        reason: str,
        description: str,
        priority: str = "medium",
    ) -> str:
        """
        Create a support ticket and persist its priority.

        Args:
            customer_id: Customer associated with the ticket.
            session_id: Conversation session associated with the ticket.
            reason: Reason for creating the ticket.
            description: Details of the customer's issue.
            priority: Ticket priority: low, medium, high, or urgent.

        Returns:
            The generated ticket ID.
        """
        allowed_priorities = {
            "low",
            "medium",
            "high",
            "urgent",
        }

        normalized_priority = (priority or "medium").strip().lower()

        if normalized_priority not in allowed_priorities:
            normalized_priority = "medium"

        ticket_id = "IA-" + secrets.token_hex(4).upper()

        self.store.create_ticket(
            ticket_id=ticket_id,
            customer_id=customer_id,
            session_id=session_id,
            reason=reason,
            description=description,
            priority=normalized_priority,
        )

        return ticket_id

    def get_customer_ticket(
        self,
        ticket_id: str,
        authenticated_customer_id: str,
    ):
        """
        Retrieve a ticket only if it belongs to the authenticated customer.
        """
        return self.store.get_ticket(
            ticket_id=ticket_id,
            customer_id=authenticated_customer_id,
        )
