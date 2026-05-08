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


# ---------------------------------------------------------------------------
# Bug #9 — nested activities (Deliverable → KeyActivity → ServiceActivity)
# ---------------------------------------------------------------------------
import pytest
from apps.services.views import _parse_nested_activities_post


class TestParseNestedActivitiesPost:
    def test_empty_post_returns_empty_dict(self):
        assert _parse_nested_activities_post({}) == {}

    def test_single_kact_with_actions(self):
        post = {
            "kact-0-0-name": "Topografía",
            "kact-0-0-order": "1",
            "kact-0-0-id": "",
            "act-0-0-0-name": "Importar dwg",
            "act-0-0-0-order": "1",
            "act-0-0-0-responsible_role": "5",
            "act-0-0-0-estimated_hours": "2",
            "act-0-0-1-name": "Levantar topografía",
            "act-0-0-1-order": "2",
        }
        result = _parse_nested_activities_post(post)
        assert 0 in result
        assert len(result[0]) == 1
        kact = result[0][0]
        assert kact["name"] == "Topografía"
        assert len(kact["actions"]) == 2
        assert kact["actions"][0]["name"] == "Importar dwg"
        assert kact["actions"][1]["name"] == "Levantar topografía"

    def test_unaligned_indices(self):
        # JS may produce non-consecutive indices (e.g. user removed kact-0-1)
        post = {
            "kact-0-0-name": "A",
            "kact-0-2-name": "C",  # gap at index 1
        }
        result = _parse_nested_activities_post(post)
        assert len(result[0]) == 2
        assert result[0][0]["index"] == 0
        assert result[0][1]["index"] == 2

    def test_multiple_deliverables(self):
        post = {
            "kact-0-0-name": "K1",
            "kact-1-0-name": "K2",
            "kact-3-0-name": "K3",  # JS-added, di=3 even though formset only had 2
        }
        result = _parse_nested_activities_post(post)
        assert set(result.keys()) == {0, 1, 3}

    def test_delete_flag_propagates(self):
        post = {
            "kact-0-0-name": "X",
            "kact-0-0-DELETE": "1",
            "kact-0-0-id": "42",
        }
        result = _parse_nested_activities_post(post)
        assert result[0][0]["delete"] is True
        assert result[0][0]["id"] == "42"


class TestServiceTemplateFormPreservesNestedOnError:
    """Bug #9: when validation fails, nested activities the user typed must reappear."""

    def test_create_with_invalid_form_keeps_nested_in_context(self, authenticated_client, db):
        url = reverse("services:servicetemplate_create")
        # Missing required `category` → form invalid; we still send nested kact data.
        data = {
            "code": "TEST-D9-1",
            "name": "Bug9 Service",
            # category intentionally omitted to force validation failure
            "deliverables-TOTAL_FORMS": "1",
            "deliverables-INITIAL_FORMS": "0",
            "deliverables-MIN_NUM_FORMS": "0",
            "deliverables-MAX_NUM_FORMS": "1000",
            "deliverables-0-name": "Modelo 3D",
            "deliverables-0-unit": "Proyecto",
            "deliverables-0-quantity": "1",
            "kact-0-TOTAL": "1",
            "kact-0-0-name": "Creación de topografía",
            "kact-0-0-order": "1",
            "act-0-0-TOTAL": "1",
            "act-0-0-0-name": "Importar dwg a Revit",
            "act-0-0-0-order": "1",
        }
        resp = authenticated_client.post(url, data)
        assert resp.status_code == 200  # re-render due to invalid form
        ctx = resp.context
        assert "nested_activities_data" in ctx
        nested = ctx["nested_activities_data"]
        assert 0 in nested
        assert nested[0][0]["name"] == "Creación de topografía"
        assert nested[0][0]["actions"][0]["name"] == "Importar dwg a Revit"
