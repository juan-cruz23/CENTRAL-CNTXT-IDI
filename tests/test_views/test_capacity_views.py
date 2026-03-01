import pytest
from decimal import Decimal
from django.urls import reverse

from tests.factories import (
    CapacityAlertFactory,
    ProjectAllocationFactory,
    ProjectFactory,
    RoleFactory,
    TeamMemberCapacityFactory,
    UserFactory,
)
from apps.capacity.models import ProjectAllocation


# ---------------------------------------------------------------------------
# CapacityOverviewView
# ---------------------------------------------------------------------------
class TestCapacityOverviewView:
    url = reverse("capacity:overview")

    def test_anonymous_redirects(self, client):
        resp = client.get(self.url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client):
        resp = authenticated_client.get(self.url)
        assert resp.status_code == 200
        assert "capacity/overview.html" in [t.name for t in resp.templates]

    def test_context_overview(self, authenticated_client):
        TeamMemberCapacityFactory()
        resp = authenticated_client.get(self.url)
        assert "overview" in resp.context

    def test_overview_with_allocation(self, authenticated_client, user):
        cap = TeamMemberCapacityFactory(user=user)
        ProjectAllocationFactory(user=user)
        resp = authenticated_client.get(self.url)
        overview = resp.context["overview"]
        assert len(overview) >= 1


# ---------------------------------------------------------------------------
# CapacityHeatmapView
# ---------------------------------------------------------------------------
class TestCapacityHeatmapView:
    url = reverse("capacity:heatmap")

    def test_anonymous_redirects(self, client):
        resp = client.get(self.url)
        assert resp.status_code == 302

    def test_authenticated_get_html(self, authenticated_client):
        resp = authenticated_client.get(self.url)
        assert resp.status_code == 200
        assert "capacity/heatmap.html" in [t.name for t in resp.templates]

    def test_json_endpoint(self, authenticated_client):
        ProjectAllocationFactory()
        resp = authenticated_client.get(self.url, HTTP_ACCEPT="application/json")
        assert resp.status_code == 200
        assert resp["Content-Type"] == "application/json"
        data = resp.json()
        assert "data" in data

    def test_json_data_structure(self, authenticated_client):
        ProjectAllocationFactory()
        resp = authenticated_client.get(self.url, HTTP_ACCEPT="application/json")
        data = resp.json()["data"]
        assert len(data) >= 1
        entry = data[0]
        for key in ("user", "project", "start_date", "weekly_hours", "allocation_pct"):
            assert key in entry


# ---------------------------------------------------------------------------
# AllocationMatrixView
# ---------------------------------------------------------------------------
class TestAllocationMatrixView:
    url = reverse("capacity:matrix")

    def test_anonymous_redirects(self, client):
        resp = client.get(self.url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client):
        resp = authenticated_client.get(self.url)
        assert resp.status_code == 200
        assert "capacity/matrix.html" in [t.name for t in resp.templates]

    def test_context_keys(self, authenticated_client):
        resp = authenticated_client.get(self.url)
        assert "users" in resp.context
        assert "projects" in resp.context


# ---------------------------------------------------------------------------
# CapacityAlertListView
# ---------------------------------------------------------------------------
class TestCapacityAlertListView:
    url = reverse("capacity:alerts")

    def test_anonymous_redirects(self, client):
        resp = client.get(self.url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client):
        CapacityAlertFactory()
        resp = authenticated_client.get(self.url)
        assert resp.status_code == 200
        assert "capacity/alerts.html" in [t.name for t in resp.templates]

    def test_shows_only_unresolved(self, authenticated_client):
        CapacityAlertFactory(is_resolved=False)
        CapacityAlertFactory(is_resolved=True)
        resp = authenticated_client.get(self.url)
        alerts = resp.context["alerts"]
        assert all(not a.is_resolved for a in alerts)


# ---------------------------------------------------------------------------
# AllocationCreateView
# ---------------------------------------------------------------------------
class TestAllocationCreateView:
    url = reverse("capacity:allocate")

    def test_anonymous_redirects(self, client):
        resp = client.get(self.url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client):
        resp = authenticated_client.get(self.url)
        assert resp.status_code == 200
        assert "capacity/allocate.html" in [t.name for t in resp.templates]

    def test_valid_post(self, authenticated_client):
        u = UserFactory()
        proj = ProjectFactory()
        role = RoleFactory()
        data = {
            "user": u.pk,
            "project": proj.pk,
            "role": role.pk,
            "start_date": "2026-01-01",
            "weekly_hours": "20",
            "allocation_pct": "50",
        }
        resp = authenticated_client.post(self.url, data)
        assert resp.status_code == 302
        assert ProjectAllocation.objects.filter(user=u, project=proj).exists()

    def test_invalid_post(self, authenticated_client):
        resp = authenticated_client.post(self.url, {})
        assert resp.status_code == 200
