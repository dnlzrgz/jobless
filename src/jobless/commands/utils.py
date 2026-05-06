def resolve_field(new, existing):
    """
    Return the correct value when updating an optional field.
    """
    if new is None:
        return existing

    if new == "":
        return None

    return new
