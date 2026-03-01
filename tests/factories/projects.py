import factory
from decimal import Decimal
from factory.django import DjangoModelFactory
from apps.projects.models import Client, Project, ProjectPhaseInstance, ServiceInstance, Milestone
from tests.factories.accounts import UserFactory
from tests.factories.organizations import BusinessUnitFactory, OperativeLineFactory
from tests.factories.services import ProjectCategoryFactory, ProjectPhaseFactory


class ClientFactory(DjangoModelFactory):
    class Meta:
        model = Client

    name = factory.Faker("name", locale="es_CO")
    company = factory.Faker("company", locale="es_CO")
    category = "BLACK"
    email = factory.Faker("email")
    phone = factory.Faker("phone_number", locale="es_CO")


class ProjectFactory(DjangoModelFactory):
    class Meta:
        model = Project

    code = factory.Sequence(lambda n: f"{200 + n}")
    name = factory.Faker("sentence", nb_words=3, locale="es_CO")
    client = factory.SubFactory(ClientFactory)
    category = factory.SubFactory(ProjectCategoryFactory)
    status = "ACTIVE"
    business_unit = factory.SubFactory(BusinessUnitFactory)
    operative_line = factory.SubFactory(OperativeLineFactory)
    leader = factory.SubFactory(UserFactory)
    total_value = Decimal("40000000.00")
    iva_rate = Decimal("19.00")
    planned_start_date = factory.Faker("date_this_year")
    planned_end_date = factory.Faker("future_date")


class ProjectPhaseInstanceFactory(DjangoModelFactory):
    class Meta:
        model = ProjectPhaseInstance

    project = factory.SubFactory(ProjectFactory)
    phase = factory.SubFactory(ProjectPhaseFactory)
    order = factory.Sequence(lambda n: n + 1)
    total_value = Decimal("10000000.00")


class ServiceInstanceFactory(DjangoModelFactory):
    class Meta:
        model = ServiceInstance

    project = factory.SubFactory(ProjectFactory)
    phase_instance = factory.SubFactory(ProjectPhaseInstanceFactory)
    code = factory.Sequence(lambda n: f"D{n}.1")
    name = factory.Faker("sentence", nb_words=5, locale="es_CO")
    quantity = Decimal("1.00")
    unit_price = Decimal("2000000.00")
    total_value = Decimal("2000000.00")
    incidence_pct = Decimal("10.00")
    margin_pct = Decimal("20.00")
    projected_hours = Decimal("20.00")


class MilestoneFactory(DjangoModelFactory):
    class Meta:
        model = Milestone

    project = factory.SubFactory(ProjectFactory)
    code = factory.Sequence(lambda n: f"HITO {n}")
    name = factory.Sequence(lambda n: f"Entrega Fase {n}")
    milestone_type = "PHASE_DELIVERY"
    planned_date = factory.Faker("future_date")
