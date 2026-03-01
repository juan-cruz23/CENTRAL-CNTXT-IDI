import pytest
from django.urls import reverse

from tests.factories import (
    ProjectCategoryFactory,
    ProjectPhaseFactory,
    ServiceTemplateFactory,
)
from apps.services.models import ServiceTemplate


# ---------------------------------------------------------------------------
# ProjectCategoryListView
# ---------------------------------------------------------------------------
class TestProjectCategoryListView:
    url = reverse("services:category_list")

    def test_anonymous_redirects(self, client):
        resp = client.get(self.url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client):
        ProjectCategoryFactory()
        resp = authenticated_client.get(self.url)
        assert resp.status_code == 200
        assert "services/projectcategory_list.html" in [t.name for t in resp.templates]

    def test_context_categories(self, authenticated_client):
        ProjectCategoryFactory()
        resp = authenticated_client.get(self.url)
        assert "categories" in resp.context or "projectcategory_list" in resp.context


# ---------------------------------------------------------------------------
# ProjectPhaseListView
# ---------------------------------------------------------------------------
class TestProjectPhaseListView:
    url = reverse("services:phase_list")

    def test_anonymous_redirects(self, client):
        resp = client.get(self.url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client):
        ProjectPhaseFactory()
        resp = authenticated_client.get(self.url)
        assert resp.status_code == 200
        assert "services/projectphase_list.html" in [t.name for t in resp.templates]

    def test_context_phases(self, authenticated_client):
        ProjectPhaseFactory()
        resp = authenticated_client.get(self.url)
        assert "phases" in resp.context or "projectphase_list" in resp.context


# ---------------------------------------------------------------------------
# ServiceTemplateListView
# ---------------------------------------------------------------------------
class TestServiceTemplateListView:
    url = reverse("services:servicetemplate_list")

    def test_anonymous_redirects(self, client):
        resp = client.get(self.url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client):
        ServiceTemplateFactory()
        resp = authenticated_client.get(self.url)
        assert resp.status_code == 200
        assert "services/servicetemplate_list.html" in [t.name for t in resp.templates]

    def test_context_service_templates(self, authenticated_client):
        ServiceTemplateFactory()
        resp = authenticated_client.get(self.url)
        assert "service_templates" in resp.context or "servicetemplate_list" in resp.context


# ---------------------------------------------------------------------------
# ServiceTemplateDetailView
# ---------------------------------------------------------------------------
class TestServiceTemplateDetailView:
    def test_anonymous_redirects(self, client, db):
        st = ServiceTemplateFactory()
        url = reverse("services:servicetemplate_detail", kwargs={"pk": st.pk})
        resp = client.get(url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client):
        st = ServiceTemplateFactory()
        url = reverse("services:servicetemplate_detail", kwargs={"pk": st.pk})
        resp = authenticated_client.get(url)
        assert resp.status_code == 200
        assert "services/servicetemplate_detail.html" in [t.name for t in resp.templates]

    def test_not_found(self, authenticated_client):
        url = reverse("services:servicetemplate_detail", kwargs={"pk": 99999})
        resp = authenticated_client.get(url)
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# ServiceTemplateCreateView
# ---------------------------------------------------------------------------
class TestServiceTemplateCreateView:
    url = reverse("services:servicetemplate_create")

    def test_anonymous_redirects(self, client):
        resp = client.get(self.url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client):
        resp = authenticated_client.get(self.url)
        assert resp.status_code == 200
        assert "services/servicetemplate_form.html" in [t.name for t in resp.templates]

    def test_valid_post(self, authenticated_client):
        cat = ProjectCategoryFactory()
        phase = ProjectPhaseFactory()
        data = {
            "code": "STMP01",
            "name": "Servicio Test",
            "category": cat.pk,
            "phase": phase.pk,
            "base_unit_price": "1000000",
            "estimated_hours": "40",
            "estimated_days": "5",
            "target_margin_pct": "20",
            "is_active": "on",
        }
        resp = authenticated_client.post(self.url, data)
        assert resp.status_code == 302
        assert ServiceTemplate.objects.filter(code="STMP01").exists()

    def test_invalid_post(self, authenticated_client):
        resp = authenticated_client.post(self.url, {})
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# ServiceTemplateUpdateView
# ---------------------------------------------------------------------------
class TestServiceTemplateUpdateView:
    def test_anonymous_redirects(self, client, db):
        st = ServiceTemplateFactory()
        url = reverse("services:servicetemplate_update", kwargs={"pk": st.pk})
        resp = client.get(url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client):
        st = ServiceTemplateFactory()
        url = reverse("services:servicetemplate_update", kwargs={"pk": st.pk})
        resp = authenticated_client.get(url)
        assert resp.status_code == 200

    def test_valid_post_updates(self, authenticated_client):
        st = ServiceTemplateFactory()
        url = reverse("services:servicetemplate_update", kwargs={"pk": st.pk})
        data = {
            "code": st.code,
            "name": "Nombre Actualizado",
            "category": st.category.pk,
            "phase": st.phase.pk,
            "base_unit_price": "2000000",
            "estimated_hours": "50",
            "estimated_days": "6",
            "target_margin_pct": "25",
            "is_active": "on",
        }
        resp = authenticated_client.post(url, data)
        assert resp.status_code == 302
        st.refresh_from_db()
        assert st.name == "Nombre Actualizado"


# ---------------------------------------------------------------------------
# ServiceTemplateDeleteView
# ---------------------------------------------------------------------------
class TestServiceTemplateDeleteView:
    def test_anonymous_redirects(self, client, db):
        st = ServiceTemplateFactory()
        url = reverse("services:servicetemplate_delete", kwargs={"pk": st.pk})
        resp = client.get(url)
        assert resp.status_code == 302

    def test_authenticated_get_confirm(self, authenticated_client):
        st = ServiceTemplateFactory()
        url = reverse("services:servicetemplate_delete", kwargs={"pk": st.pk})
        resp = authenticated_client.get(url)
        assert resp.status_code == 200
        assert "services/servicetemplate_confirm_delete.html" in [t.name for t in resp.templates]

    def test_post_deletes(self, authenticated_client):
        st = ServiceTemplateFactory()
        url = reverse("services:servicetemplate_delete", kwargs={"pk": st.pk})
        resp = authenticated_client.post(url)
        assert resp.status_code == 302
        assert not ServiceTemplate.objects.filter(pk=st.pk).exists()
