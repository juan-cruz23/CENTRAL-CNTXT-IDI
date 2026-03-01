import pytest
from decimal import Decimal
from domain.metrics.calculators import EVMCalculator
from tests.factories.projects import ProjectFactory, ProjectPhaseInstanceFactory, ServiceInstanceFactory


@pytest.mark.django_db
class TestEVMCalculator:
    def test_basic_evm_calculation(self):
        project = ProjectFactory(total_value=Decimal("40000000"))
        phase = ProjectPhaseInstanceFactory(project=project)

        # Create services with known values
        # total_value is computed as quantity * unit_price on save
        ServiceInstanceFactory(
            project=project,
            phase_instance=phase,
            quantity=Decimal("1"),
            unit_price=Decimal("10000000"),
            progress_pct=Decimal("100"),
            expected_progress_pct=Decimal("100"),
            real_operative_cost=Decimal("8000000"),
        )
        ServiceInstanceFactory(
            project=project,
            phase_instance=phase,
            quantity=Decimal("1"),
            unit_price=Decimal("10000000"),
            progress_pct=Decimal("50"),
            expected_progress_pct=Decimal("100"),
            real_operative_cost=Decimal("7000000"),
        )

        calc = EVMCalculator(project)
        result = calc.calculate()

        assert result["bac"] == Decimal("40000000.00")
        # PV = 10M*100% + 10M*100% = 20M
        assert result["planned_value"] == Decimal("20000000.00")
        # EV = 10M*100% + 10M*50% = 15M
        assert result["earned_value"] == Decimal("15000000.00")
        # AC = 8M + 7M = 15M
        assert result["actual_cost"] == Decimal("15000000.00")
        # SPI = 15/20 = 0.75 (quantized to 4 decimal places)
        assert result["spi"] == Decimal("0.7500")
        # CPI = 15/15 = 1.0 (quantized to 4 decimal places)
        assert result["cpi"] == Decimal("1.0000")

    def test_zero_division_handling(self):
        project = ProjectFactory(total_value=Decimal("40000000"))
        calc = EVMCalculator(project)
        result = calc.calculate()

        assert result["spi"] == Decimal("0.0000")
        assert result["cpi"] == Decimal("0.0000")
