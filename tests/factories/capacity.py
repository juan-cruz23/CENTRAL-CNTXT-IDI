import factory
from decimal import Decimal
from factory.django import DjangoModelFactory
from apps.capacity.models import TeamMemberCapacity, ProjectAllocation, CapacityAlert
from tests.factories.accounts import UserFactory, RoleFactory
from tests.factories.projects import ProjectFactory


class TeamMemberCapacityFactory(DjangoModelFactory):
    class Meta:
        model = TeamMemberCapacity

    user = factory.SubFactory(UserFactory)
    weekly_available_hours = Decimal("40.00")
    effective_from = factory.Faker("date_this_year")
    notes = ""


class ProjectAllocationFactory(DjangoModelFactory):
    class Meta:
        model = ProjectAllocation

    user = factory.SubFactory(UserFactory)
    project = factory.SubFactory(ProjectFactory)
    role = factory.SubFactory(RoleFactory)
    start_date = factory.Faker("date_this_year")
    weekly_hours = Decimal("20.00")
    allocation_pct = Decimal("50.00")


class CapacityAlertFactory(DjangoModelFactory):
    class Meta:
        model = CapacityAlert

    user = factory.SubFactory(UserFactory)
    alert_type = "OVERLOAD"
    week_start = factory.Faker("date_this_year")
    allocated_hours = Decimal("50.00")
    available_hours = Decimal("40.00")
    is_resolved = False
