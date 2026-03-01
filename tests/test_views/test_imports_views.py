import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from tests.factories import ImportJobFactory
from apps.imports.models import ImportJob


# ---------------------------------------------------------------------------
# ImportWizardView
# ---------------------------------------------------------------------------
class TestImportWizardView:
    url = reverse("imports:wizard")

    def test_anonymous_redirects(self, client):
        resp = client.get(self.url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client):
        resp = authenticated_client.get(self.url)
        assert resp.status_code == 200
        assert "imports/wizard.html" in [t.name for t in resp.templates]

    def test_context_keys(self, authenticated_client):
        resp = authenticated_client.get(self.url)
        ctx = resp.context
        assert "source_types" in ctx
        assert "recent_jobs" in ctx


# ---------------------------------------------------------------------------
# UploadCSVView
# ---------------------------------------------------------------------------
class TestUploadCSVView:
    url = reverse("imports:upload")

    def test_anonymous_redirects(self, client):
        resp = client.get(self.url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client):
        resp = authenticated_client.get(self.url)
        assert resp.status_code == 200
        assert "imports/upload.html" in [t.name for t in resp.templates]

    def test_valid_post_creates_job(self, authenticated_client):
        csv_file = SimpleUploadedFile(
            "data.csv", b"col1,col2\nval1,val2", content_type="text/csv"
        )
        data = {
            "file": csv_file,
            "source_type": "COR_SHEET",
        }
        resp = authenticated_client.post(self.url, data, format="multipart")
        assert resp.status_code == 302
        assert ImportJob.objects.count() == 1

    def test_invalid_post_no_file(self, authenticated_client):
        data = {"source_type": "COR_SHEET"}
        resp = authenticated_client.post(self.url, data)
        assert resp.status_code == 200

    def test_redirect_to_preview(self, authenticated_client):
        csv_file = SimpleUploadedFile(
            "data.csv", b"col1,col2\nval1,val2", content_type="text/csv"
        )
        data = {"file": csv_file, "source_type": "COR_SHEET"}
        resp = authenticated_client.post(self.url, data, format="multipart")
        assert resp.status_code == 302
        job = ImportJob.objects.first()
        assert f"/importar/previa/{job.pk}/" in resp.url


# ---------------------------------------------------------------------------
# PreviewImportView
# ---------------------------------------------------------------------------
class TestPreviewImportView:
    def test_anonymous_redirects(self, client, db):
        job = ImportJobFactory()
        url = reverse("imports:preview", kwargs={"pk": job.pk})
        resp = client.get(url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client, user):
        job = ImportJobFactory(uploaded_by=user)
        url = reverse("imports:preview", kwargs={"pk": job.pk})
        resp = authenticated_client.get(url)
        assert resp.status_code == 200
        assert "imports/preview.html" in [t.name for t in resp.templates]

    def test_context_keys(self, authenticated_client, user):
        job = ImportJobFactory(uploaded_by=user)
        url = reverse("imports:preview", kwargs={"pk": job.pk})
        resp = authenticated_client.get(url)
        assert "job" in resp.context

    def test_other_user_cannot_preview(self, authenticated_client, db):
        job = ImportJobFactory()
        url = reverse("imports:preview", kwargs={"pk": job.pk})
        resp = authenticated_client.get(url)
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# ConfirmImportView
# ---------------------------------------------------------------------------
class TestConfirmImportView:
    def test_anonymous_redirects(self, client, db):
        job = ImportJobFactory()
        url = reverse("imports:confirm", kwargs={"pk": job.pk})
        resp = client.get(url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client, user):
        job = ImportJobFactory(uploaded_by=user)
        url = reverse("imports:confirm", kwargs={"pk": job.pk})
        resp = authenticated_client.get(url)
        assert resp.status_code == 200
        assert "imports/confirm.html" in [t.name for t in resp.templates]

    def test_post_wrong_status_redirects(self, authenticated_client, user):
        job = ImportJobFactory(uploaded_by=user, status="UPLOADED")
        url = reverse("imports:confirm", kwargs={"pk": job.pk})
        resp = authenticated_client.post(url)
        assert resp.status_code == 302

    def test_post_confirmed_status(self, authenticated_client, user):
        job = ImportJobFactory(uploaded_by=user, status="PREVIEWED")
        url = reverse("imports:confirm", kwargs={"pk": job.pk})
        resp = authenticated_client.post(url)
        assert resp.status_code == 302
        job.refresh_from_db()
        assert job.status in ("COMPLETED", "FAILED")
