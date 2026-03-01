import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from tests.factories import ProjectDocumentFactory, ProjectFactory
from apps.documents.models import ProjectDocument


# ---------------------------------------------------------------------------
# ProjectDocumentListView
# ---------------------------------------------------------------------------
class TestProjectDocumentListView:
    def test_anonymous_redirects(self, client, project):
        url = reverse("documents:document_list", kwargs={"project_pk": project.pk})
        resp = client.get(url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client, project):
        url = reverse("documents:document_list", kwargs={"project_pk": project.pk})
        resp = authenticated_client.get(url)
        assert resp.status_code == 200
        assert "documents/projectdocument_list.html" in [t.name for t in resp.templates]

    def test_context_keys(self, authenticated_client, project):
        ProjectDocumentFactory(project=project)
        url = reverse("documents:document_list", kwargs={"project_pk": project.pk})
        resp = authenticated_client.get(url)
        assert "project_pk" in resp.context

    def test_lists_documents(self, authenticated_client, project):
        ProjectDocumentFactory(project=project)
        ProjectDocumentFactory(project=project)
        url = reverse("documents:document_list", kwargs={"project_pk": project.pk})
        resp = authenticated_client.get(url)
        docs = resp.context.get("documents") or resp.context.get("projectdocument_list")
        assert len(docs) == 2


# ---------------------------------------------------------------------------
# ProjectDocumentCreateView
# ---------------------------------------------------------------------------
class TestProjectDocumentCreateView:
    def test_anonymous_redirects(self, client, project):
        url = reverse("documents:document_create", kwargs={"project_pk": project.pk})
        resp = client.get(url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client, project):
        url = reverse("documents:document_create", kwargs={"project_pk": project.pk})
        resp = authenticated_client.get(url)
        assert resp.status_code == 200
        assert "documents/projectdocument_form.html" in [t.name for t in resp.templates]

    def test_valid_post(self, authenticated_client, project):
        url = reverse("documents:document_create", kwargs={"project_pk": project.pk})
        test_file = SimpleUploadedFile("doc.pdf", b"PDF content", content_type="application/pdf")
        data = {
            "project": project.pk,
            "document_type": "DELIVERABLE",
            "name": "Entregable fase 1",
            "file": test_file,
        }
        resp = authenticated_client.post(url, data, format="multipart")
        assert resp.status_code == 302
        assert ProjectDocument.objects.filter(project=project).exists()

    def test_valid_post_with_link(self, authenticated_client, project):
        url = reverse("documents:document_create", kwargs={"project_pk": project.pk})
        data = {
            "project": project.pk,
            "document_type": "SUPPORT",
            "name": "Documento soporte",
            "access_link": "https://drive.google.com/example",
        }
        resp = authenticated_client.post(url, data)
        assert resp.status_code == 302

    def test_invalid_post(self, authenticated_client, project):
        url = reverse("documents:document_create", kwargs={"project_pk": project.pk})
        resp = authenticated_client.post(url, {})
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# ProjectDocumentUpdateView
# ---------------------------------------------------------------------------
class TestProjectDocumentUpdateView:
    def test_anonymous_redirects(self, client, project):
        doc = ProjectDocumentFactory(project=project)
        url = reverse("documents:document_update", kwargs={"project_pk": project.pk, "pk": doc.pk})
        resp = client.get(url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client, project):
        doc = ProjectDocumentFactory(project=project)
        url = reverse("documents:document_update", kwargs={"project_pk": project.pk, "pk": doc.pk})
        resp = authenticated_client.get(url)
        assert resp.status_code == 200

    def test_valid_post_updates(self, authenticated_client, project):
        doc = ProjectDocumentFactory(project=project)
        url = reverse("documents:document_update", kwargs={"project_pk": project.pk, "pk": doc.pk})
        data = {
            "project": project.pk,
            "document_type": "CONTRACT",
            "name": "Contrato actualizado",
        }
        resp = authenticated_client.post(url, data)
        assert resp.status_code == 302
        doc.refresh_from_db()
        assert doc.name == "Contrato actualizado"
