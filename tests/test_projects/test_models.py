import pytest
from decimal import Decimal
from tests.factories.projects import ClientFactory, ProjectFactory, ServiceInstanceFactory


@pytest.mark.django_db
class TestClient:
    def test_create_client(self):
        client = ClientFactory(name="William Zuluaga", category="BLACK")
        assert client.pk is not None
        assert str(client) == "William Zuluaga"


@pytest.mark.django_db
class TestProject:
    def test_create_project(self):
        project = ProjectFactory(code="216", name="Casa Saint Regis")
        assert project.pk is not None
        assert str(project) == "216 - Casa Saint Regis"

    def test_project_defaults(self):
        project = ProjectFactory()
        assert project.status == "ACTIVE"
        assert project.current_progress_pct == Decimal("0")
        assert project.iva_rate == Decimal("19.00")


@pytest.mark.django_db
class TestServiceInstance:
    def test_total_value_calculation(self):
        si = ServiceInstanceFactory(quantity=Decimal("2"), unit_price=Decimal("1000000"))
        # total_value should be computed on save
        assert si.total_value == Decimal("2000000.00")
