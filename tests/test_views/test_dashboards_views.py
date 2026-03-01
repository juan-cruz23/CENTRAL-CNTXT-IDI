import pytest
from django.urls import reverse

from tests.factories import (
    AlertFactory,
    PaymentMilestoneFactory,
    ProjectFactory,
    ProjectMetricSnapshotFactory,
    UserFactory,
)
from apps.organizations.models import OrganizationalSystem


# ---------------------------------------------------------------------------
# Executive Dashboard (home)
# ---------------------------------------------------------------------------
class TestExecutiveDashboardView:
    url = reverse("dashboards:home")

    def test_anonymous_redirects(self, client):
        resp = client.get(self.url)
        assert resp.status_code == 302
        assert "/cuentas/login/" in resp.url

    def test_authenticated_get(self, authenticated_client):
        resp = authenticated_client.get(self.url)
        assert resp.status_code == 200
        assert "dashboards/home.html" in [t.name for t in resp.templates]

    def test_context_keys(self, authenticated_client):
        ProjectFactory()
        resp = authenticated_client.get(self.url)
        ctx = resp.context
        for key in (
            "active_projects", "total_portfolio_value", "avg_progress",
            "avg_spi", "avg_cpi", "projects_at_risk", "projects_at_risk_count",
            "recent_alerts", "projects",
        ):
            assert key in ctx

    def test_active_projects_counted(self, authenticated_client):
        ProjectFactory(status="ACTIVE")
        ProjectFactory(status="COMPLETED")
        resp = authenticated_client.get(self.url)
        assert resp.context["active_projects"] == 1


# ---------------------------------------------------------------------------
# Portfolio Dashboard
# ---------------------------------------------------------------------------
class TestPortfolioDashboardView:
    url = reverse("dashboards:portfolio")

    def test_anonymous_redirects(self, client):
        resp = client.get(self.url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client):
        resp = authenticated_client.get(self.url)
        assert resp.status_code == 200
        assert "dashboards/portfolio.html" in [t.name for t in resp.templates]

    def test_context_projects(self, authenticated_client):
        ProjectFactory()
        resp = authenticated_client.get(self.url)
        assert "projects" in resp.context


# ---------------------------------------------------------------------------
# Project Dashboard
# ---------------------------------------------------------------------------
class TestProjectDashboardView:
    def test_anonymous_redirects(self, client, project):
        url = reverse("dashboards:project", kwargs={"project_pk": project.pk})
        resp = client.get(url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client, project):
        url = reverse("dashboards:project", kwargs={"project_pk": project.pk})
        resp = authenticated_client.get(url)
        assert resp.status_code == 200
        assert "dashboards/project.html" in [t.name for t in resp.templates]

    def test_context_keys(self, authenticated_client, full_project):
        url = reverse("dashboards:project", kwargs={"project_pk": full_project.pk})
        resp = authenticated_client.get(url)
        ctx = resp.context
        for key in ("project", "phases", "latest_snapshot", "payment_milestones", "payment_summary"):
            assert key in ctx

    def test_not_found(self, authenticated_client):
        url = reverse("dashboards:project", kwargs={"project_pk": 99999})
        resp = authenticated_client.get(url)
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# System Dashboard
# ---------------------------------------------------------------------------
class TestSystemDashboardView:
    def test_anonymous_redirects(self, client, organizational_system):
        url = reverse("dashboards:system", kwargs={"system_code": organizational_system.code})
        resp = client.get(url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client, organizational_system):
        url = reverse("dashboards:system", kwargs={"system_code": organizational_system.code})
        resp = authenticated_client.get(url)
        assert resp.status_code == 200
        assert "dashboards/system.html" in [t.name for t in resp.templates]

    def test_context_keys(self, authenticated_client, organizational_system):
        url = reverse("dashboards:system", kwargs={"system_code": organizational_system.code})
        resp = authenticated_client.get(url)
        assert "system" in resp.context
        assert "projects" in resp.context

    def test_system_not_found(self, authenticated_client):
        url = reverse("dashboards:system", kwargs={"system_code": "NONEXIST"})
        resp = authenticated_client.get(url)
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Leader Dashboard
# ---------------------------------------------------------------------------
class TestLeaderDashboardView:
    url = reverse("dashboards:leader")

    def test_anonymous_redirects(self, client):
        resp = client.get(self.url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client):
        resp = authenticated_client.get(self.url)
        assert resp.status_code == 200
        assert "dashboards/leader.html" in [t.name for t in resp.templates]

    def test_context_keys(self, authenticated_client):
        resp = authenticated_client.get(self.url)
        ctx = resp.context
        for key in ("my_projects", "team_allocations", "team_capacity", "upcoming_milestones"):
            assert key in ctx


# ---------------------------------------------------------------------------
# API: portfolio_data_api
# ---------------------------------------------------------------------------
class TestPortfolioDataApi:
    url = reverse("dashboards:portfolio_data")

    def test_anonymous_redirects(self, client):
        resp = client.get(self.url)
        assert resp.status_code == 302

    def test_returns_json(self, authenticated_client):
        ProjectFactory()
        resp = authenticated_client.get(self.url)
        assert resp.status_code == 200
        assert resp["Content-Type"] == "application/json"
        data = resp.json()
        assert isinstance(data, list)

    def test_json_fields(self, authenticated_client):
        ProjectFactory()
        resp = authenticated_client.get(self.url)
        data = resp.json()
        assert len(data) >= 1
        entry = data[0]
        for key in ("code", "name", "client", "status", "progress", "total_value", "leader"):
            assert key in entry


# ---------------------------------------------------------------------------
# API: cashflow_data_api
# ---------------------------------------------------------------------------
class TestCashflowDataApi:
    def test_anonymous_redirects(self, client, project):
        url = reverse("dashboards:cashflow_data", kwargs={"project_pk": project.pk})
        resp = client.get(url)
        assert resp.status_code == 302

    def test_returns_json(self, authenticated_client, project):
        PaymentMilestoneFactory(project=project)
        url = reverse("dashboards:cashflow_data", kwargs={"project_pk": project.pk})
        resp = authenticated_client.get(url)
        assert resp.status_code == 200
        data = resp.json()
        for key in ("labels", "proposed", "executed", "collected"):
            assert key in data
