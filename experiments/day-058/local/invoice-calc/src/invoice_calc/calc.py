"""Invoice total calculation."""

TAX_RATE = 0.10


def total_with_tax(subtotal: float, rate: float = TAX_RATE) -> float:
    """Return subtotal plus tax, rounded to 2 decimal places."""
    return round(subtotal * (1 + rate), 2)
