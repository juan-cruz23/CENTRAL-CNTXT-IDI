import pytest
from tests.factories.services import ServiceTemplateFactory, ProjectCategoryFactory, ProjectPhaseFactory


@pytest.mark.django_db
class TestServiceTemplate:
    def test_create_service_template(self):
        template = ServiceTemplateFactory(code="D0.1", name="Diagnóstico del Proyecto")
        assert template.pk is not None
        assert str(template) == "D0.1 - Diagnóstico del Proyecto"
