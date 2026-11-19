"""Basic tests for the database and tool layer. Run with: pytest"""

from app.database import load_seed
from app.tools import run_tool


def setup_module():
    """Load sample data before the tests run."""
    load_seed()


def test_lookup_customer_found():
    result = run_tool("lookup_customer", {"email": "asha@example.com"})
    assert result["name"] == "Asha Rao"


def test_lookup_customer_missing():
    result = run_tool("lookup_customer", {"email": "nobody@example.com"})
    assert "error" in result


def test_list_orders():
    result = run_tool("list_orders", {"customer_id": 1})
    assert len(result["orders"]) == 2


def test_check_order_status():
    result = run_tool("check_order_status", {"order_id": 3})
    assert result["status"] == "processing"


def test_create_and_list_tickets():
    created = run_tool(
        "create_support_ticket",
        {"customer_id": 3, "subject": "Test", "description": "Test ticket"},
    )
    assert created["status"] == "open"
    tickets = run_tool("list_tickets", {"customer_id": 3})
    assert len(tickets["tickets"]) >= 1


def test_unknown_tool():
    assert "error" in run_tool("does_not_exist", {})