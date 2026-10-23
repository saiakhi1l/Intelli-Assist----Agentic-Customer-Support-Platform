from intelli_assist.tickets import TicketRepository
class Settings:
    database_enabled=False

def test_ticket_round_trip():
    repo=TicketRepository(Settings())
    item=repo.create("Login issue","Cannot sign in","cust-1","high")
    assert item["ticket_id"].startswith("TKT-")
    assert repo.get(item["ticket_id"])["subject"]=="Login issue"
    assert repo.get("missing") is None
