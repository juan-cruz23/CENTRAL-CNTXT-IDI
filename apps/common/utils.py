import re
from datetime import date
from decimal import Decimal, InvalidOperation


def parse_cop_currency(value: str) -> Decimal:
    """
    Parse a Colombian peso currency string to Decimal.

    Handles formats like:
        "$40.000.000"    -> Decimal("40000000")
        "$664.431,00"    -> Decimal("664431.00")
        "1.200.000"      -> Decimal("1200000")
        "40000000"       -> Decimal("40000000")

    Colombian format uses dots as thousands separators and
    comma as the decimal separator.
    """
    if not value or not isinstance(value, str):
        return Decimal("0")

    cleaned = value.strip()
    # Remove currency symbol and whitespace
    cleaned = cleaned.replace("$", "").replace(" ", "")

    if not cleaned:
        return Decimal("0")

    # Check if there is a comma (decimal separator in Colombian format)
    if "," in cleaned:
        # Split on comma: left part has thousands dots, right part is decimals
        parts = cleaned.split(",")
        integer_part = parts[0].replace(".", "")
        decimal_part = parts[1] if len(parts) > 1 else "0"
        cleaned = f"{integer_part}.{decimal_part}"
    else:
        # No comma: dots are thousands separators only
        cleaned = cleaned.replace(".", "")

    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return Decimal("0")


def parse_colombian_date(value: str) -> date | None:
    """
    Parse a Colombian date string (DD/MM/YYYY) to a date object.

    Handles formats like:
        "1/10/2025"   -> date(2025, 10, 1)
        "01/10/2025"  -> date(2025, 10, 1)

    Returns None if the string cannot be parsed.
    """
    if not value or not isinstance(value, str):
        return None

    cleaned = value.strip()
    match = re.match(r"^(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})$", cleaned)
    if not match:
        return None

    try:
        day = int(match.group(1))
        month = int(match.group(2))
        year = int(match.group(3))
        return date(year, month, day)
    except (ValueError, OverflowError):
        return None


def parse_colombian_percentage(value: str) -> Decimal:
    """
    Parse a Colombian percentage string to Decimal.

    Handles formats like:
        "8,33%"    -> Decimal("8.33")
        "100,00%"  -> Decimal("100.00")
        "50%"      -> Decimal("50")

    Returns the numeric value (e.g., 8.33, not 0.0833).
    """
    if not value or not isinstance(value, str):
        return Decimal("0")

    cleaned = value.strip()
    cleaned = cleaned.replace("%", "").strip()
    cleaned = cleaned.replace(",", ".")

    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return Decimal("0")


def format_cop(value: Decimal) -> str:
    """
    Format a Decimal value as a Colombian peso currency string.

    Examples:
        Decimal("40000000")   -> "$40.000.000"
        Decimal("664431.00")  -> "$664.431"
        Decimal("1200000.50") -> "$1.200.000,50"
    """
    if value is None:
        return "$0"

    # Ensure we work with a Decimal
    if not isinstance(value, Decimal):
        try:
            value = Decimal(str(value))
        except (InvalidOperation, TypeError):
            return "$0"

    # Split into integer and decimal parts
    sign = "-" if value < 0 else ""
    abs_value = abs(value)
    str_value = str(abs_value)

    if "." in str_value:
        integer_str, decimal_str = str_value.split(".")
        # Remove trailing zeros from decimal part
        decimal_str = decimal_str.rstrip("0")
    else:
        integer_str = str_value
        decimal_str = ""

    # Format integer part with dots as thousands separators
    reversed_digits = integer_str[::-1]
    groups = [reversed_digits[i : i + 3] for i in range(0, len(reversed_digits), 3)]
    formatted_integer = ".".join(groups)[::-1]

    if decimal_str:
        return f"{sign}${formatted_integer},{decimal_str}"
    else:
        return f"{sign}${formatted_integer}"
