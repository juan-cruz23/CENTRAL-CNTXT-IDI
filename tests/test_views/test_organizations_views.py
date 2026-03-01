import pytest
from django.urls import reverse

from tests.factories import (
    BusinessUnitFactory,
    OperativeLineFactory,
    OrganizationalSystemFactory,
)


# ---------------------------------------------------------------------------
# OrganizationalSystemListView
# ---------------------------------------------------------------------------
class TestOrganizationalSystemListView:
    url = reverse("organizations:system_list")

    def test_anonymous_redirects(self, client):
        resp = client.get(self.url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client):
        OrganizationalSystemFactory()
        resp = authenticated_client.get(self.url)
        assert resp.status_code == 200
        assert "organizations/organizationalsystem_list.html" in [t.name for t in resp.templates]

    def test_context_systems(self, authenticated_client):
        OrganizationalSystemFactory()
        resp = authenticated_client.get(self.url)
        assert "systems" in resp.context or "organizationalsystem_list" in resp.context

    def test_lists_all_systems(self, authenticated_client):
        OrganizationalSystemFactory()
        OrganizationalSystemFactory()
        resp = authenticated_client.get(self.url)
        systems = resp.context.get("systems") or resp.context.get("organizationalsystem_list")
        assert len(systems) == 2


# ---------------------------------------------------------------------------
# BusinessUnitListView
# ---------------------------------------------------------------------------
class TestBusinessUnitListView:
    url = reverse("organizations:businessunit_list")

    def test_anonymous_redirects(self, client):
        resp = client.get(self.url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client):
        BusinessUnitFactory()
        resp = authenticated_client.get(self.url)
        assert resp.status_code == 200
        assert "organizations/businessunit_list.html" in [t.name for t in resp.templates]

    def test_context_business_units(self, authenticated_client):
        BusinessUnitFactory()
        resp = authenticated_client.get(self.url)
        assert "business_units" in resp.context or "businessunit_list" in resp.context


# ---------------------------------------------------------------------------
# OperativeLineListView
# ---------------------------------------------------------------------------
class TestOperativeLineListView:
    url = reverse("organizations:operativeline_list")

    def test_anonymous_redirects(self, client):
        resp = client.get(self.url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client):
        OperativeLineFactory()
        resp = authenticated_client.get(self.url)
        assert resp.status_code == 200
        assert "organizations/operativeline_list.html" in [t.name for t in resp.templates]

    def test_context_operative_lines(self, authenticated_client):
        OperativeLineFactory()
        resp = authenticated_client.get(self.url)
        assert "operative_lines" in resp.context or "operativeline_list" in resp.context
