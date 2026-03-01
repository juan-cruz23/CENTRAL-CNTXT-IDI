import factory
from factory.django import DjangoModelFactory
from apps.services.models import ProjectCategory, ProjectPhase, ServiceTemplate


class ProjectCategoryFactory(DjangoModelFactory):
    class Meta:
        model = ProjectCategory

    code = factory.Sequence(lambda n: f"CAT{n}")
    name = factory.Sequence(lambda n: f"Categoría {n}")
    is_active = True


class ProjectPhaseFactory(DjangoModelFactory):
    class Meta:
        model = ProjectPhase

    number = factory.Sequence(lambda n: n + 1)
    name = factory.LazyAttribute(lambda o: f"Fase {o.number}")


class ServiceTemplateFactory(DjangoModelFactory):
    class Meta:
        model = ServiceTemplate

    code = factory.Sequence(lambda n: f"S{n:03d}")
    name = factory.Faker("sentence", nb_words=5, locale="es_CO")
    category = factory.SubFactory(ProjectCategoryFactory)
    phase = factory.SubFactory(ProjectPhaseFactory)
    base_unit_price = factory.Faker("pydecimal", left_digits=7, right_digits=2, positive=True)
    estimated_hours = factory.Faker("pydecimal", left_digits=3, right_digits=2, positive=True, min_value=1, max_value=100)
    target_margin_pct = 20
