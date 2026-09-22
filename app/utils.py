def normalize_category(value: str) -> str:
    """Collapse whitespace and lowercase a category value.

    Applied both when writing (schema validation) and when filtering
    (query params), so "Food", " food ", and "FOOD" are treated as the
    same category instead of silently fragmenting spend_by_category.
    """
    return " ".join(value.split()).lower()
