import factory
from factory.django import DjangoModelFactory
from apps.organizations.models import OrganizationalSystem, BusinessUnit, OperativeLine


class OrganizationalSystemFactory(DjangoModelFactory):
    class Meta:
        model = OrganizationalSystem

    code = factory.Sequence(lambda n: f"SYS{n}")
    name = factory.Sequence(lambda n: f"Sistema {n}")
    analogy = factory.Faker("word", locale="es_CO")
    is_active = True


class BusinessUnitFactory(DjangoModelFactory):
    class Meta:
        model = BusinessUnit

    code = factory.Sequence(lambda n: f"BU{n}")
    name = factory.Sequence(lambda n: f"Unidad {n}")
    is_active = True


class OperativeLineFactory(DjangoModelFactory):
    class Meta:
        model = OperativeLine

    code = factory.Sequence(lambda n: f"OL{n}")
    name = factory.Sequence(lambda n: f"Línea Operativa {n}")
    business_unit = factory.SubFactory(BusinessUnitFactory)
    is_active = True
