"""Tool functions for customer support operations."""

from app.database import (
    get_customer_by_email,
    get_orders_for_customer,
    get_order_status,
    create_ticket,
    get_tickets_for_customer,
)


def lookup_customer(email: str) -> dict:
    """Look up a customer record by their email address.

    Args:
        email: The customer's email address.

    Returns:
        The customer profile, or an error dictionary if not found.
    """
    customer = get_customer_by_email(email)
    if customer is None:
        return {"error": "No customer found with that email."}
    return customer


def list_orders(customer_id: int) -> dict:
    """Retrieve all past and present orders placed by a customer.

    Args:
        customer_id: The unique ID of the customer.

    Returns:
        A dictionary containing the list of orders.
    """
    orders = get_orders_for_customer(customer_id)
    return {"orders": orders}


def check_order_status(order_id: int) -> dict:
    """Check the details and delivery status of a specific order.

    Args:
        order_id: The unique ID of the order.

    Returns:
        The order details, or an error dictionary if not found.
    """
    order = get_order_status(order_id)
    if order is None:
        return {"error": "Order not found."}
    return order


def create_support_ticket(customer_id: int, subject: str, description: str) -> dict:
    """Create a new support ticket for a customer issue.

    Args:
        customer_id: The unique ID of the customer.
        subject: Brief topic or title of the issue.
        description: Detailed description of the support request.

    Returns:
        The created ticket record.
    """
    return create_ticket(customer_id, subject, description)


def list_tickets(customer_id: int) -> dict:
    """Retrieve all support tickets opened by a specific customer.

    Args:
        customer_id: The unique ID of the customer.

    Returns:
        A dictionary containing the list of tickets.
    """
    tickets = get_tickets_for_customer(customer_id)
    return {"tickets": tickets}


# Handler dispatch mapping (used by unit tests and direct execution)
TOOL_HANDLERS = {
    "lookup_customer": lookup_customer,
    "list_orders": list_orders,
    "check_order_status": check_order_status,
    "create_support_ticket": create_support_ticket,
    "list_tickets": list_tickets,
}


def run_tool(name: str, args: dict) -> dict:
    """Execute a tool handler by name with supplied arguments."""
    if name not in TOOL_HANDLERS:
        return {"error": f"Unknown tool: {name}"}

    handler = TOOL_HANDLERS[name]
    try:
        return handler(**args)
    except Exception as e:
        return {"error": f"Tool failed: {str(e)}"}
