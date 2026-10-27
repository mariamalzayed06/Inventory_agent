from .models import Item


def add_item(name: str, quantity: int) -> dict:
    """
    Add a given quantity of an item to inventory.
    If the item doesn't exist yet, it is created.
    """
    item, created = Item.objects.get_or_create(name=name.lower())
    item.quantity += quantity
    item.save()
    return {
        "name": item.name,
        "quantity": item.quantity,
        "created": created,
    }


def remove_item(name: str, quantity: int) -> dict:
    """
    Remove a given quantity of an item from inventory.
    Returns an error message if the item doesn't exist
    or if there isn't enough stock.
    """
    try:
        item = Item.objects.get(name=name.lower())
    except Item.DoesNotExist:
        return {"error": f"No item named '{name}' in inventory."}

    if item.quantity < quantity:
        return {
            "error": f"Not enough stock. Only {item.quantity} {name}(s) available."
        }

    item.quantity -= quantity
    item.save()
    return {"name": item.name, "quantity": item.quantity}


def check_stock(name: str) -> dict:
    """
    Return the current quantity of a given item.
    """
    try:
        item = Item.objects.get(name=name.lower())
    except Item.DoesNotExist:
        return {"name": name, "quantity": 0, "note": "Item not found in inventory."}

    return {"name": item.name, "quantity": item.quantity}


def list_items() -> dict:
    """
    Return all items currently in inventory.
    """
    items = Item.objects.all()
    return {
        "items": [{"name": i.name, "quantity": i.quantity} for i in items]
    }

tool_declarations = [
    {
        "name": "add_item",
        "description": "Add a given quantity of an item to inventory. If the item doesn't exist yet, it is created.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the item, e.g. 'screwdriver'."
                },
                "quantity": {
                    "type": "integer",
                    "description": "The number of units to add."
                }
            },
            "required": ["name", "quantity"]
        }
    },
    {
        "name": "remove_item",
        "description": "Remove a given quantity of an item from inventory. Fails if the item doesn't exist or there isn't enough stock.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the item, e.g. 'screwdriver'."
                },
                "quantity": {
                    "type": "integer",
                    "description": "The number of units to remove."
                }
            },
            "required": ["name", "quantity"]
        }
    },
    {
        "name": "check_stock",
        "description": "Get the current quantity in stock for a specific item.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the item to check, e.g. 'hammer'."
                }
            },
            "required": ["name"]
        }
    },
    {
        "name": "list_items",
        "description": "List all items currently in inventory along with their quantities.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    }
]