import pytest
from datetime import date
from apps.financials.models import ColombianHoliday


@pytest.mark.django_db
class TestColombianHoliday:
    def test_is_holiday(self):
        ColombianHoliday.objects.create(date=date(2025, 12, 25), name="Navidad")
        assert ColombianHoliday.is_holiday(date(2025, 12, 25)) is True
        assert ColombianHoliday.is_holiday(date(2025, 12, 26)) is False

    def test_holidays_in_range(self):
        ColombianHoliday.objects.create(date=date(2025, 12, 25), name="Navidad")
        ColombianHoliday.objects.create(date=date(2026, 1, 1), name="Año Nuevo")
        qs = ColombianHoliday.holidays_in_range(date(2025, 12, 1), date(2025, 12, 31))
        assert qs.count() == 1
