import factory
from factory.django import DjangoModelFactory
from apps.documents.models import ProjectDocument
from tests.factories.projects import ProjectFactory


class ProjectDocumentFactory(DjangoModelFactory):
    class Meta:
        model = ProjectDocument

    project = factory.SubFactory(ProjectFactory)
    document_type = "DELIVERABLE"
    name = factory.Faker("sentence", nb_words=4, locale="es_CO")
    access_link = factory.Faker("url")
    delivery_date = factory.Faker("date_this_year")
