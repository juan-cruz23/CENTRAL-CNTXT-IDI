import pytest
from django.urls import reverse

from tests.factories import ProjectFactory, ProjectMetricSnapshotFactory


# ---------------------------------------------------------------------------
# ProjectMetricsView
# ---------------------------------------------------------------------------
class TestProjectMetricsView:
    def test_anonymous_redirects(self, client, project):
        url = reverse("metrics:project_metrics", kwargs={"project_pk": project.pk})
        resp = client.get(url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client, project):
        url = reverse("metrics:project_metrics", kwargs={"project_pk": project.pk})
        resp = authenticated_client.get(url)
        assert resp.status_code == 200
        assert "metrics/project_metrics.html" in [t.name for t in resp.templates]

    def test_context_keys(self, authenticated_client, project):
        ProjectMetricSnapshotFactory(project=project)
        url = reverse("metrics:project_metrics", kwargs={"project_pk": project.pk})
        resp = authenticated_client.get(url)
        ctx = resp.context
        assert "project" in ctx
        assert "snapshot" in ctx

    def test_context_with_snapshot(self, authenticated_client, project):
        ProjectMetricSnapshotFactory(project=project)
        url = reverse("metrics:project_metrics", kwargs={"project_pk": project.pk})
        resp = authenticated_client.get(url)
        assert resp.context["snapshot"] is not None

    def test_context_without_snapshot(self, authenticated_client, project):
        url = reverse("metrics:project_metrics", kwargs={"project_pk": project.pk})
        resp = authenticated_client.get(url)
        assert resp.context["snapshot"] is None


# ---------------------------------------------------------------------------
# SCurveDataView
# ---------------------------------------------------------------------------
class TestSCurveDataView:
    def test_anonymous_redirects(self, client, project):
        url = reverse("metrics:scurve_data", kwargs={"project_pk": project.pk})
        resp = client.get(url)
        assert resp.status_code == 302

    def test_returns_json(self, authenticated_client, project):
        ProjectMetricSnapshotFactory(project=project)
        url = reverse("metrics:scurve_data", kwargs={"project_pk": project.pk})
        resp = authenticated_client.get(url)
        assert resp.status_code == 200
        assert resp["Content-Type"] == "application/json"
        data = resp.json()
        for key in ("dates", "planned_value", "earned_value", "actual_cost"):
            assert key in data

    def test_empty_data(self, authenticated_client, project):
        url = reverse("metrics:scurve_data", kwargs={"project_pk": project.pk})
        resp = authenticated_client.get(url)
        assert resp.status_code == 200
        data = resp.json()
        assert data["dates"] == []


# ---------------------------------------------------------------------------
# MetricHistoryView
# ---------------------------------------------------------------------------
class TestMetricHistoryView:
    def test_anonymous_redirects(self, client, project):
        url = reverse("metrics:metric_history", kwargs={"project_pk": project.pk})
        resp = client.get(url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client, project):
        ProjectMetricSnapshotFactory(project=project)
        url = reverse("metrics:metric_history", kwargs={"project_pk": project.pk})
        resp = authenticated_client.get(url)
        assert resp.status_code == 200
        assert "metrics/metric_history.html" in [t.name for t in resp.templates]

    def test_context_keys(self, authenticated_client, project):
        url = reverse("metrics:metric_history", kwargs={"project_pk": project.pk})
        resp = authenticated_client.get(url)
        assert "project" in resp.context
