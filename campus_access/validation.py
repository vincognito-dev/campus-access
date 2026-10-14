import re
from typing import Any


def validate_id(value: Any) -> bool:
    """Return True for integer request ids >= 1 or numeric strings representing such ints."""
    if isinstance(value, int):
        return value >= 1
    if isinstance(value, str) and value.isdigit():
        return int(value) >= 1
    return False


def validate_fellow_id(value: Any) -> bool:
    """Fellow ids follow the pattern FEL-#### (4 digits)."""
    if not isinstance(value, str):
        return False
    return bool(re.match(r"^FEL-\d{4}$", value))


def validate_card_type(value: Any) -> bool:
    """Acceptable card types: student, staff, visitor."""
    if not isinstance(value, str):
        return False
    return value in ("student", "staff", "visitor")
