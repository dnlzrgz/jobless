from datetime import datetime, date


def resolve_field(new, existing):
    """
    Return the correct value when updating an optional field.
    """
    if new is None:
        return existing

    if new == "":
        return None

    return new


def date_serializer(obj):
    """
    JSON serializer for objects that are serializable by default.
    """
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    raise TypeError(f"type {type(obj)} is not serializable")
