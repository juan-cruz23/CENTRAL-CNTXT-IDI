import factory
from decimal import Decimal
from factory.django import DjangoModelFactory
from apps.metrics.models import ProjectMetricSnapshot
from tests.factories.projects import ProjectFactory


class ProjectMetricSnapshotFactory(DjangoModelFactory):
    class Meta:
        model = ProjectMetricSnapshot

    project = factory.SubFactory(ProjectFactory)
    snapshot_date = factory.Faker("date_this_year")
    bac = Decimal("40000000.00")
    planned_value = Decimal("20000000.00")
    earned_value = Decimal("18000000.00")
    actual_cost = Decimal("17000000.00")
    spi = Decimal("0.9000")
    cpi = Decimal("1.0588")
    schedule_variance = Decimal("-2000000.00")
    cost_variance = Decimal("1000000.00")
    eac = Decimal("37777777.78")
    etc = Decimal("20777777.78")
    vac = Decimal("2222222.22")
    overall_progress_pct = Decimal("45.00")
    expected_progress_pct = Decimal("50.00")
    schedule_deviation_pct = Decimal("-10.00")
    total_revenue = Decimal("18000000.00")
    total_costs = Decimal("17000000.00")
    projected_margin_pct = Decimal("5.56")
