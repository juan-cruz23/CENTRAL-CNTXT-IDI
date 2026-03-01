import pytest
from decimal import Decimal
from datetime import date
from apps.common.utils import parse_cop_currency, parse_colombian_date, parse_colombian_percentage, format_cop


class TestParseCOPCurrency:
    def test_standard_format(self):
        assert parse_cop_currency("$40.000.000") == Decimal("40000000")

    def test_with_decimals(self):
        assert parse_cop_currency("$664.431,00") == Decimal("664431.00")

    def test_with_iva(self):
        assert parse_cop_currency("$3.200.000,00") == Decimal("3200000.00")

    def test_zero(self):
        assert parse_cop_currency("$0") == Decimal("0")

    def test_negative(self):
        assert parse_cop_currency("-$12.000.000") == Decimal("-12000000")

    def test_empty_or_none(self):
        assert parse_cop_currency("") == Decimal("0")
        assert parse_cop_currency(None) == Decimal("0")


class TestParseColombianDate:
    def test_standard_format(self):
        assert parse_colombian_date("1/10/2025") == date(2025, 10, 1)

    def test_padded_format(self):
        assert parse_colombian_date("01/10/2025") == date(2025, 10, 1)

    def test_empty(self):
        assert parse_colombian_date("") is None
        assert parse_colombian_date(None) is None

    def test_holiday_format(self):
        # Holidays in CSV use DD-MM-YYYY
        assert parse_colombian_date("24-03-2025") == date(2025, 3, 24)


class TestParseColombianPercentage:
    def test_standard(self):
        assert parse_colombian_percentage("8,33%") == Decimal("8.33")

    def test_hundred(self):
        assert parse_colombian_percentage("100,00%") == Decimal("100.00")

    def test_zero(self):
        assert parse_colombian_percentage("0,00%") == Decimal("0.00")

    def test_empty(self):
        assert parse_colombian_percentage("") == Decimal("0")


class TestFormatCOP:
    def test_millions(self):
        result = format_cop(Decimal("40000000"))
        assert result == "$40.000.000"

    def test_with_decimals(self):
        result = format_cop(Decimal("664431.00"))
        assert result == "$664.431"

    def test_zero(self):
        assert format_cop(Decimal("0")) == "$0"
