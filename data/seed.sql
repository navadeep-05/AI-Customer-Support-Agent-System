-- Sample data for local testing only. Safe to re-run with INSERT OR IGNORE.

-- Customers
INSERT OR IGNORE INTO customers (id, name, email, phone) VALUES
    (1, 'Asha Rao', 'asha@example.com', '+91-9000000001'),
    (2, 'Ravi Kumar', 'ravi@example.com', '+91-9000000002'),
    (3, 'Meena Iyer', 'meena@example.com', NULL);

-- Orders
INSERT OR IGNORE INTO orders (id, customer_id, product, status, total, created_at) VALUES
    (1, 1, 'Wireless Headphones', 'delivered', 2499.00, '2026-01-10 10:00:00'),
    (2, 1, 'Phone Case', 'shipped', 599.00, '2026-02-15 09:30:00'),
    (3, 2, 'Smart Watch', 'processing', 8999.00, '2026-03-01 14:20:00'),
    (4, 2, 'Keyboard', 'delivered', 1299.00, '2026-03-05 11:45:00'),
    (5, 3, 'Laptop Stand', 'cancelled', 1850.00, '2026-03-10 16:00:00');

-- Tickets
INSERT OR IGNORE INTO tickets (id, customer_id, subject, description, status, created_at) VALUES
    (1, 1, 'Headphones left ear not working', 'Left earbud has no sound since day one.', 'open', '2026-02-20 12:00:00'),
    (2, 2, 'Refund for cancelled watch', 'Order 3 was cancelled but refund not received.', 'resolved', '2026-03-03 08:15:00');
