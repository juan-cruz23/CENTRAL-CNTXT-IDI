import pytest
from django.urls import reverse

from tests.factories import (
    ClientFactory,
    ProjectFactory,
    ProjectPhaseInstanceFactory,
    ServiceInstanceFactory,
    ProjectCategoryFactory,
    BusinessUnitFactory,
    OperativeLineFactory,
    UserFactory,
)
from apps.projects.models import Client, Project


# ---------------------------------------------------------------------------
# ProjectListView
# ---------------------------------------------------------------------------
class TestProjectListView:
    url = reverse("projects:list")

    def test_anonymous_redirects(self, client):
        resp = client.get(self.url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client):
        resp = authenticated_client.get(self.url)
        assert resp.status_code == 200
        assert "projects/project_list.html" in [t.name for t in resp.templates]

    def test_context_keys(self, authenticated_client):
        resp = authenticated_client.get(self.url)
        ctx = resp.context
        for key in ("projects", "status_choices", "current_status", "search_query"):
            assert key in ctx

    def test_filter_by_status(self, authenticated_client):
        ProjectFactory(status="ACTIVE")
        ProjectFactory(status="COMPLETED")
        resp = authenticated_client.get(self.url + "?status=ACTIVE")
        assert all(p.status == "ACTIVE" for p in resp.context["projects"])

    def test_search_by_name(self, authenticated_client):
        ProjectFactory(name="Proyecto Único Especial")
        ProjectFactory(name="Otro Proyecto")
        resp = authenticated_client.get(self.url + "?q=Único")
        projects = list(resp.context["projects"])
        assert len(projects) == 1

    def test_pagination(self, authenticated_client):
        for _ in range(30):
            ProjectFactory()
        resp = authenticated_client.get(self.url)
        assert resp.context["is_paginated"] is True


# ---------------------------------------------------------------------------
# ProjectDetailView
# ---------------------------------------------------------------------------
class TestProjectDetailView:
    def test_anonymous_redirects(self, client, project):
        url = reverse("projects:detail", kwargs={"pk": project.pk})
        resp = client.get(url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client, project):
        url = reverse("projects:detail", kwargs={"pk": project.pk})
        resp = authenticated_client.get(url)
        assert resp.status_code == 200
        assert "projects/project_detail.html" in [t.name for t in resp.templates]

    def test_context_project(self, authenticated_client, project):
        url = reverse("projects:detail", kwargs={"pk": project.pk})
        resp = authenticated_client.get(url)
        assert resp.context["project"].pk == project.pk

    def test_not_found(self, authenticated_client):
        url = reverse("projects:detail", kwargs={"pk": 99999})
        resp = authenticated_client.get(url)
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# ProjectCreateView
# ---------------------------------------------------------------------------
class TestProjectCreateView:
    url = reverse("projects:create")

    def test_anonymous_redirects(self, client):
        resp = client.get(self.url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client):
        resp = authenticated_client.get(self.url)
        assert resp.status_code == 200
        assert "projects/project_form.html" in [t.name for t in resp.templates]

    def test_valid_post_creates_project(self, authenticated_client, db):
        cl = ClientFactory()
        data = {
            "code": "999",
            "name": "Proyecto Test",
            "client": cl.pk,
            "status": "PLANNING",
            "access_type": "STANDARD",
            "country": "Colombia",
            "iva_rate": "19",
        }
        resp = authenticated_client.post(self.url, data)
        assert resp.status_code == 302
        assert Project.objects.filter(code="999").exists()

    def test_invalid_post_returns_form(self, authenticated_client):
        resp = authenticated_client.post(self.url, {})
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# ProjectUpdateView
# ---------------------------------------------------------------------------
class TestProjectUpdateView:
    def test_anonymous_redirects(self, client, project):
        url = reverse("projects:update", kwargs={"pk": project.pk})
        resp = client.get(url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client, project):
        url = reverse("projects:update", kwargs={"pk": project.pk})
        resp = authenticated_client.get(url)
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# ServiceInstanceListView
# ---------------------------------------------------------------------------
class TestServiceInstanceListView:
    def test_anonymous_redirects(self, client, project_with_phase):
        proj, phase = project_with_phase
        url = reverse("projects:phase_services", kwargs={"pk": proj.pk, "phase_pk": phase.pk})
        resp = client.get(url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client, project_with_phase):
        proj, phase = project_with_phase
        ServiceInstanceFactory(project=proj, phase_instance=phase)
        url = reverse("projects:phase_services", kwargs={"pk": proj.pk, "phase_pk": phase.pk})
        resp = authenticated_client.get(url)
        assert resp.status_code == 200
        assert "projects/service_instance_list.html" in [t.name for t in resp.templates]

    def test_context_keys(self, authenticated_client, project_with_phase):
        proj, phase = project_with_phase
        url = reverse("projects:phase_services", kwargs={"pk": proj.pk, "phase_pk": phase.pk})
        resp = authenticated_client.get(url)
        assert "project" in resp.context
        assert "phase_instance" in resp.context


# ---------------------------------------------------------------------------
# ServiceInstanceUpdateView
# ---------------------------------------------------------------------------
class TestServiceInstanceUpdateView:
    def test_anonymous_redirects(self, client, service_instance):
        si = service_instance
        url = reverse("projects:service_update", kwargs={"pk": si.project.pk, "si_pk": si.pk})
        resp = client.get(url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client, service_instance):
        si = service_instance
        url = reverse("projects:service_update", kwargs={"pk": si.project.pk, "si_pk": si.pk})
        resp = authenticated_client.get(url)
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# ClientListView
# ---------------------------------------------------------------------------
class TestClientListView:
    url = reverse("projects:client_list")

    def test_anonymous_redirects(self, client):
        resp = client.get(self.url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client):
        resp = authenticated_client.get(self.url)
        assert resp.status_code == 200
        assert "projects/client_list.html" in [t.name for t in resp.templates]

    def test_context_keys(self, authenticated_client):
        resp = authenticated_client.get(self.url)
        ctx = resp.context
        for key in ("clients", "category_choices", "current_category", "search_query"):
            assert key in ctx

    def test_search(self, authenticated_client):
        ClientFactory(name="Cliente Alfa")
        ClientFactory(name="Cliente Beta")
        resp = authenticated_client.get(self.url + "?q=Alfa")
        assert len(list(resp.context["clients"])) == 1


# ---------------------------------------------------------------------------
# ClientCreateView
# ---------------------------------------------------------------------------
class TestClientCreateView:
    url = reverse("projects:client_create")

    def test_anonymous_redirects(self, client):
        resp = client.get(self.url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client):
        resp = authenticated_client.get(self.url)
        assert resp.status_code == 200
        assert "projects/client_form.html" in [t.name for t in resp.templates]

    def test_valid_post(self, authenticated_client):
        data = {
            "name": "Nuevo Cliente",
            "company": "Empresa Test",
            "category": "BLACK",
            "email": "test@example.com",
            "phone": "3001234567",
        }
        resp = authenticated_client.post(self.url, data)
        assert resp.status_code == 302
        assert Client.objects.filter(name="Nuevo Cliente").exists()

    def test_invalid_post(self, authenticated_client):
        resp = authenticated_client.post(self.url, {})
        assert resp.status_code == 200
