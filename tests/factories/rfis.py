import factory
from factory.django import DjangoModelFactory
from apps.rfis.models import RFI
from tests.factories.projects import ProjectFactory


class RFIFactory(DjangoModelFactory):
    class Meta:
        model = RFI

    project = factory.SubFactory(ProjectFactory)
    code = factory.Sequence(lambda n: f"RFI-{n:03d}")
    observations = factory.Faker("paragraph", locale="es_CO")
    status = "OPEN"
