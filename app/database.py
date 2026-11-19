"""SQLite data access layer for the customer support agent.

Provides database initialization, connection handling, and data access
functions. All queries use parameterized inputs to prevent SQL injection.
"""

import os
import sqlite3
from typing import Any, Dict, List, Optional
from app.config import DATABASE_PATH


def get_connection() -> sqlite3.Connection:
    """Open and configure a SQLite database connection.

    Args:
        None

    Returns:
        sqlite3.Connection: Configured connection with Row factory and foreign keys enabled.
    """
    # Ensure parent directory exists before creating or opening the database file
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    # SQLite has foreign key constraints disabled by default; enable them per connection
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db() -> None:
    """Initialize the database schema if tables do not exist.

    Args:
        None

    Returns:
        None
    """
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL REFERENCES customers(id),
            product TEXT NOT NULL,
            status TEXT NOT NULL,
            total REAL NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL REFERENCES customers(id),
            subject TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL DEFAULT 'open',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    conn.commit()
    conn.close()
    return None


def get_customer_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Retrieve customer record matching the given email address.

    Args:
        email (str): The email address of the customer to search for.

    Returns:
        Optional[Dict[str, Any]]: Dictionary containing customer columns, or None if not found.
    """
    conn = get_connection()
    cursor = conn.execute(
        "SELECT id, name, email, phone, created_at FROM customers WHERE email = ?",
        (email,),
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_orders_for_customer(customer_id: int) -> List[Dict[str, Any]]:
    """Retrieve all orders placed by a specific customer, newest first.

    Args:
        customer_id (int): The ID of the customer whose orders to fetch.

    Returns:
        List[Dict[str, Any]]: List of order records as dictionaries, or empty list if none found.
    """
    conn = get_connection()
    cursor = conn.execute(
        "SELECT id, customer_id, product, status, total, created_at FROM orders WHERE customer_id = ? ORDER BY created_at DESC, id DESC",
        (customer_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    # Convert sqlite3.Row objects into plain dicts for serializability and caller use
    return [dict(row) for row in rows]


def get_order_status(order_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve the status and details of a single order by order ID.

    Args:
        order_id (int): The ID of the order to look up.

    Returns:
        Optional[Dict[str, Any]]: Dictionary containing order columns, or None if not found.
    """
    conn = get_connection()
    cursor = conn.execute(
        "SELECT id, customer_id, product, status, total, created_at FROM orders WHERE id = ?",
        (order_id,),
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def create_ticket(
    customer_id: int, subject: str, description: Optional[str]
) -> Dict[str, Any]:
    """Create a new support ticket and return the created record.

    Args:
        customer_id (int): The ID of the customer creating the ticket.
        subject (str): Brief subject or summary of the ticket.
        description (Optional[str]): Detailed description of the customer issue.

    Returns:
        Dict[str, Any]: The newly inserted ticket record as a dictionary.
    """
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO tickets (customer_id, subject, description) VALUES (?, ?, ?)",
        (customer_id, subject, description),
    )
    conn.commit()
    # Retrieve the auto-generated primary key from the insert operation
    new_id = cursor.lastrowid
    cursor = conn.execute(
        "SELECT id, customer_id, subject, description, status, created_at FROM tickets WHERE id = ?",
        (new_id,),
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row)


def get_tickets_for_customer(customer_id: int) -> List[Dict[str, Any]]:
    """Retrieve all support tickets for a customer, newest first.

    Args:
        customer_id (int): The ID of the customer whose tickets to fetch.

    Returns:
        List[Dict[str, Any]]: List of ticket records as dictionaries, or empty list if none found.
    """
    conn = get_connection()
    cursor = conn.execute(
        "SELECT id, customer_id, subject, description, status, created_at FROM tickets WHERE customer_id = ? ORDER BY created_at DESC, id DESC",
        (customer_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    # Convert sqlite3.Row objects into plain dicts for serializability and caller use
    return [dict(row) for row in rows]


def load_seed() -> None:
    """Load sample seed data into the database from seed.sql.

    Args:
        None

    Returns:
        None
    """
    # Build the path to seed.sql relative to this file's location
    seed_path = os.path.join(os.path.dirname(__file__), "..", "data", "seed.sql")

    # Ensure tables are created first before inserting data
    init_db()

    # Read the SQL statements from the seed file
    with open(seed_path, "r", encoding="utf-8") as f:
        sql_text = f.read()

    # Execute the seed script and close the connection
    conn = get_connection()
    conn.executescript(sql_text)
    conn.close()
