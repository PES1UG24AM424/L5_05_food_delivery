
"""Manage food delivery orders, menus, and daily revenue."""

# pylint: disable=global-statement

import json
from datetime import datetime
from pathlib import Path

orders = {}
NEXT_ID = 1
menu = {}

VALID_STATUSES = {"placed", "cooking", "out_for_delivery", "delivered"}
DEFAULT_MENU = {
    "pizza": 250,
    "burger": 150,
    "fries": 90,
    "coke": 40,
}


def create_order(customer, items, order_history=None):
    """Create an order and optionally record its ID in order history."""
    global NEXT_ID

    if not isinstance(customer, str) or not customer.strip():
        raise ValueError("Customer name cannot be empty.")

    if not isinstance(items, list) or not items:
        raise ValueError("An order must contain at least one item.")

    if any(item not in menu for item in items):
        raise ValueError("Order contains an item not present in the menu.")

    total = sum(menu[item] for item in items)

    orders[NEXT_ID] = {
        "customer": customer.strip(),
        "items": items.copy(),
        "total": total,
        "status": "placed",
    }

    if order_history is None:
        order_history = []

    order_history.append(NEXT_ID)
    NEXT_ID += 1

    return order_history[-1]


def update_order_status(order_id, status):
    """Update an order only when its ID and status are valid."""
    if order_id not in orders:
        raise ValueError(f"Order {order_id} does not exist.")

    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid order status: {status}")

    orders[order_id]["status"] = status


def read_menu_config(file="menu.json"):
    """Load menu prices from JSON or use the default menu."""
    global menu

    try:
        with Path(file).open("r", encoding="utf-8") as menu_file:
            loaded_menu = json.load(menu_file)

        if not isinstance(loaded_menu, dict):
            raise ValueError("Menu must be a JSON object.")

        for name, price in loaded_menu.items():
            if (
                not isinstance(name, str)
                or not isinstance(price, (int, float))
                or isinstance(price, bool)
                or price < 0
            ):
                raise ValueError(
                    "Menu items must have non-negative numeric prices."
                )

        menu = loaded_menu

    except (OSError, json.JSONDecodeError, ValueError):
        menu = DEFAULT_MENU.copy()


def daily_revenue():
    """Return revenue from delivered orders."""
    return sum(
        order["total"]
        for order in orders.values()
        if order["status"] == "delivered"
    )


def backup_orders(file="orders.json"):
    """Back up orders in a JSON file."""
    data = {
        str(order_id): order
        for order_id, order in orders.items()
    }

    with Path(file).open("w", encoding="utf-8") as backup_file:
        json.dump(data, backup_file, indent=4)


def is_valid_order_data(order_id, order):
    """Check whether a restored order has the expected fields and values."""
    if not order_id.isdigit() or not isinstance(order, dict):
        return False

    customer = order.get("customer")
    items = order.get("items")
    total = order.get("total")
    status = order.get("status")

    if not isinstance(customer, str) or not customer.strip():
        return False

    if not isinstance(items, list):
        return False

    if (
        not isinstance(total, (int, float))
        or isinstance(total, bool)
        or total < 0
    ):
        return False

    if status not in VALID_STATUSES:
        return False

    return True


def restore_orders(file="orders.json"):
    """Restore orders from a JSON backup."""
    global orders, NEXT_ID

    with Path(file).open("r", encoding="utf-8") as backup_file:
        data = json.load(backup_file)

    if not isinstance(data, dict):
        raise ValueError("Order backup must be a JSON object.")

    restored = {}

    for order_id, order in data.items():
        if not is_valid_order_data(order_id, order):
            raise ValueError("Invalid order data in backup.")

        restored[int(order_id)] = order

    orders = restored
    NEXT_ID = max(orders, default=0) + 1


def print_queue():
    """Print all orders in the delivery queue."""
    print(f"Order queue at {datetime.now()}")

    for order_id, order in orders.items():
        print(
            order_id,
            order["customer"],
            order["status"],
            order["total"],
        )


def main():
    """Run a small demonstration of the delivery system."""
    read_menu_config()

    order_history = []
    first_order = create_order(
        "Asha", ["pizza", "coke"], order_history
    )
    second_order = create_order("Ravi", ["burger"])

    update_order_status(first_order, "delivered")

    try:
        update_order_status(second_order, "teleported")
    except ValueError as error:
        print(f"Status update rejected: {error}")

    print("Revenue today:", daily_revenue())

    backup_orders()
    restore_orders()
    print_queue()


if __name__ == "__main__":
    main()
