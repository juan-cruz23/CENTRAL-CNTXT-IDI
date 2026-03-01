import factory
from decimal import Decimal
from factory.django import DjangoModelFactory
from apps.financials.models import PaymentMilestone, ProfitabilitySummary
from tests.factories.projects import ProjectFactory


class PaymentMilestoneFactory(DjangoModelFactory):
    class Meta:
        model = PaymentMilestone

    project = factory.SubFactory(ProjectFactory)
    concept = factory.Sequence(lambda n: f"Pago {n}")
    proposed_value = Decimal("5000000.00")
    iva_value = Decimal("950000.00")
    incidence_pct = Decimal("25.00")
    status = "PENDING"
    executed_value = Decimal("0.00")


class ProfitabilitySummaryFactory(DjangoModelFactory):
    class Meta:
        model = ProfitabilitySummary

    project = factory.SubFactory(ProjectFactory)
    milestone_name = factory.Sequence(lambda n: f"Entrega {n}")
    value = Decimal("10000000.00")
    months_invested = Decimal("2.00")
    analysis_costs = Decimal("1000000.00")
    total_costs = Decimal("3000000.00")
    expenses = Decimal("500000.00")
    revenue = Decimal("10000000.00")
    utility = Decimal("6500000.00")
    margin_pct = Decimal("65.00")
