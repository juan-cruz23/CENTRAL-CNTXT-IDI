import pytest
from django.urls import reverse

from tests.factories import ProjectFactory, RFIFactory, UserFactory
from apps.rfis.models import RFI


# ---------------------------------------------------------------------------
# RFIListView
# ---------------------------------------------------------------------------
class TestRFIListView:
    def test_anonymous_redirects(self, client, project):
        url = reverse("rfis:rfi_list", kwargs={"project_pk": project.pk})
        resp = client.get(url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client, project):
        url = reverse("rfis:rfi_list", kwargs={"project_pk": project.pk})
        resp = authenticated_client.get(url)
        assert resp.status_code == 200
        assert "rfis/rfi_list.html" in [t.name for t in resp.templates]

    def test_context_keys(self, authenticated_client, project):
        url = reverse("rfis:rfi_list", kwargs={"project_pk": project.pk})
        resp = authenticated_client.get(url)
        assert "project_pk" in resp.context

    def test_lists_rfis(self, authenticated_client, project):
        RFIFactory(project=project)
        RFIFactory(project=project)
        url = reverse("rfis:rfi_list", kwargs={"project_pk": project.pk})
        resp = authenticated_client.get(url)
        rfis = resp.context.get("rfis") or resp.context.get("rfi_list")
        assert len(rfis) == 2


# ---------------------------------------------------------------------------
# RFIDetailView
# ---------------------------------------------------------------------------
class TestRFIDetailView:
    def test_anonymous_redirects(self, client, project):
        rfi = RFIFactory(project=project)
        url = reverse("rfis:rfi_detail", kwargs={"project_pk": project.pk, "pk": rfi.pk})
        resp = client.get(url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client, project):
        rfi = RFIFactory(project=project)
        url = reverse("rfis:rfi_detail", kwargs={"project_pk": project.pk, "pk": rfi.pk})
        resp = authenticated_client.get(url)
        assert resp.status_code == 200
        assert "rfis/rfi_detail.html" in [t.name for t in resp.templates]

    def test_context_rfi(self, authenticated_client, project):
        rfi = RFIFactory(project=project)
        url = reverse("rfis:rfi_detail", kwargs={"project_pk": project.pk, "pk": rfi.pk})
        resp = authenticated_client.get(url)
        assert "rfi" in resp.context or "object" in resp.context

    def test_not_found(self, authenticated_client, project):
        url = reverse("rfis:rfi_detail", kwargs={"project_pk": project.pk, "pk": 99999})
        resp = authenticated_client.get(url)
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# RFICreateView
# ---------------------------------------------------------------------------
class TestRFICreateView:
    def test_anonymous_redirects(self, client, project):
        url = reverse("rfis:rfi_create", kwargs={"project_pk": project.pk})
        resp = client.get(url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client, project):
        url = reverse("rfis:rfi_create", kwargs={"project_pk": project.pk})
        resp = authenticated_client.get(url)
        assert resp.status_code == 200
        assert "rfis/rfi_form.html" in [t.name for t in resp.templates]

    def test_valid_post(self, authenticated_client, project):
        url = reverse("rfis:rfi_create", kwargs={"project_pk": project.pk})
        data = {
            "project": project.pk,
            "code": "RFI-TEST-001",
            "observations": "Solicitud de prueba",
            "time_invested_hours": "2.5",
            "status": "OPEN",
        }
        resp = authenticated_client.post(url, data)
        assert resp.status_code == 302
        assert RFI.objects.filter(code="RFI-TEST-001").exists()

    def test_invalid_post(self, authenticated_client, project):
        url = reverse("rfis:rfi_create", kwargs={"project_pk": project.pk})
        resp = authenticated_client.post(url, {})
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# RFIUpdateView
# ---------------------------------------------------------------------------
class TestRFIUpdateView:
    def test_anonymous_redirects(self, client, project):
        rfi = RFIFactory(project=project)
        url = reverse("rfis:rfi_update", kwargs={"project_pk": project.pk, "pk": rfi.pk})
        resp = client.get(url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client, project):
        rfi = RFIFactory(project=project)
        url = reverse("rfis:rfi_update", kwargs={"project_pk": project.pk, "pk": rfi.pk})
        resp = authenticated_client.get(url)
        assert resp.status_code == 200

    def test_valid_post_updates(self, authenticated_client, project):
        rfi = RFIFactory(project=project)
        url = reverse("rfis:rfi_update", kwargs={"project_pk": project.pk, "pk": rfi.pk})
        data = {
            "project": project.pk,
            "code": rfi.code,
            "observations": "Observaciones actualizadas",
            "time_invested_hours": "5",
            "status": "IN_PROGRESS",
        }
        resp = authenticated_client.post(url, data)
        assert resp.status_code == 302
        rfi.refresh_from_db()
        assert rfi.status == "IN_PROGRESS"
