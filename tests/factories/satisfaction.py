import factory
from decimal import Decimal
from factory.django import DjangoModelFactory
from apps.satisfaction.models import SatisfactionMeasurement, SatisfactionSurvey
from tests.factories.projects import ProjectFactory


class SatisfactionMeasurementFactory(DjangoModelFactory):
    class Meta:
        model = SatisfactionMeasurement

    project = factory.SubFactory(ProjectFactory)
    measurement_date = factory.Faker("date_this_year")
    observed_emotion_pct = Decimal("80.00")
    spontaneous_phrase_pct = Decimal("75.00")
    symbolic_object_pct = Decimal("85.00")


class SatisfactionSurveyFactory(DjangoModelFactory):
    class Meta:
        model = SatisfactionSurvey

    measurement = factory.SubFactory(SatisfactionMeasurementFactory)
    general_sensation = Decimal("80.00")
    clarity_and_support = Decimal("75.00")
    personal_effort = Decimal("85.00")
    team_relationship = Decimal("90.00")
    confidence = Decimal("80.00")
    perceived_value = Decimal("85.00")
