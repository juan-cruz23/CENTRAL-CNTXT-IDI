import factory
from factory.django import DjangoModelFactory
from apps.notifications.models import Alert
from tests.factories.projects import ProjectFactory


class AlertFactory(DjangoModelFactory):
    class Meta:
        model = Alert

    project = factory.SubFactory(ProjectFactory)
    severity = "WARNING"
    category = "SCHEDULE_DEVIATION"
    title = factory.Faker("sentence", nb_words=5, locale="es_CO")
    message = factory.Faker("paragraph", locale="es_CO")
    is_read = False
    is_resolved = False
