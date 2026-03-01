from decimal import Decimal

from django import template

from apps.common.utils import format_cop

register = template.Library()


@register.filter(name="cop_format")
def cop_format(value):
    """
    Format a numeric value as a Colombian peso currency string.

    Usage in templates:
        {{ amount|cop_format }}
    """
    if value is None:
        return "$0"
    if not isinstance(value, Decimal):
        try:
            value = Decimal(str(value))
        except Exception:
            return "$0"
    return format_cop(value)


@register.filter(name="percentage_format")
def percentage_format(value):
    """
    Format a numeric value as a percentage string with Colombian notation.

    Usage in templates:
        {{ rate|percentage_format }}
        Output: "8,33%"
    """
    if value is None:
        return "0%"
    try:
        decimal_value = Decimal(str(value))
    except Exception:
        return "0%"

    str_value = str(decimal_value)
    # Replace dot with comma for Colombian format
    str_value = str_value.replace(".", ",")
    return f"{str_value}%"
