import pytest
from django.urls import reverse

from tests.factories import (
    PaymentMilestoneFactory,
    ProfitabilitySummaryFactory,
    ProjectFactory,
)
from apps.financials.models import PaymentMilestone


# ---------------------------------------------------------------------------
# ProjectFinancialView
# ---------------------------------------------------------------------------
class TestProjectFinancialView:
    def test_anonymous_redirects(self, client, project):
        url = reverse("financials:project_financial", kwargs={"project_pk": project.pk})
        resp = client.get(url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client, project):
        url = reverse("financials:project_financial", kwargs={"project_pk": project.pk})
        resp = authenticated_client.get(url)
        assert resp.status_code == 200
        assert "financials/project_financial.html" in [t.name for t in resp.templates]

    def test_context_keys(self, authenticated_client, project):
        PaymentMilestoneFactory(project=project)
        ProfitabilitySummaryFactory(project=project)
        url = reverse("financials:project_financial", kwargs={"project_pk": project.pk})
        resp = authenticated_client.get(url)
        ctx = resp.context
        for key in ("payment_milestones", "profitability_summaries", "project_pk"):
            assert key in ctx


# ---------------------------------------------------------------------------
# PaymentMilestoneListView
# ---------------------------------------------------------------------------
class TestPaymentMilestoneListView:
    def test_anonymous_redirects(self, client, project):
        url = reverse("financials:payment_list", kwargs={"project_pk": project.pk})
        resp = client.get(url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client, project):
        PaymentMilestoneFactory(project=project)
        url = reverse("financials:payment_list", kwargs={"project_pk": project.pk})
        resp = authenticated_client.get(url)
        assert resp.status_code == 200
        assert "financials/paymentmilestone_list.html" in [t.name for t in resp.templates]

    def test_context_keys(self, authenticated_client, project):
        url = reverse("financials:payment_list", kwargs={"project_pk": project.pk})
        resp = authenticated_client.get(url)
        assert "payment_milestones" in resp.context or "paymentmilestone_list" in resp.context
        assert "project_pk" in resp.context


# ---------------------------------------------------------------------------
# PaymentMilestoneCreateView
# ---------------------------------------------------------------------------
class TestPaymentMilestoneCreateView:
    def test_anonymous_redirects(self, client, project):
        url = reverse("financials:payment_create", kwargs={"project_pk": project.pk})
        resp = client.get(url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client, project):
        url = reverse("financials:payment_create", kwargs={"project_pk": project.pk})
        resp = authenticated_client.get(url)
        assert resp.status_code == 200
        assert "financials/paymentmilestone_form.html" in [t.name for t in resp.templates]

    def test_valid_post(self, authenticated_client, project):
        url = reverse("financials:payment_create", kwargs={"project_pk": project.pk})
        data = {
            "project": project.pk,
            "concept": "Anticipo",
            "proposed_value": "5000000",
            "iva_value": "950000",
            "incidence_pct": "25",
            "status": "PENDING",
            "discount_pct": "0",
            "discount_value": "0",
            "executed_value": "0",
            "invoice_value": "0",
            "collection_value": "0",
        }
        resp = authenticated_client.post(url, data)
        assert resp.status_code == 302
        assert PaymentMilestone.objects.filter(project=project, concept="Anticipo").exists()

    def test_invalid_post(self, authenticated_client, project):
        url = reverse("financials:payment_create", kwargs={"project_pk": project.pk})
        resp = authenticated_client.post(url, {})
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# PaymentMilestoneUpdateView
# ---------------------------------------------------------------------------
class TestPaymentMilestoneUpdateView:
    def test_anonymous_redirects(self, client, project):
        pm = PaymentMilestoneFactory(project=project)
        url = reverse("financials:payment_update", kwargs={"project_pk": project.pk, "pk": pm.pk})
        resp = client.get(url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client, project):
        pm = PaymentMilestoneFactory(project=project)
        url = reverse("financials:payment_update", kwargs={"project_pk": project.pk, "pk": pm.pk})
        resp = authenticated_client.get(url)
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# ProfitabilityOverviewView
# ---------------------------------------------------------------------------
class TestProfitabilityOverviewView:
    url = reverse("financials:profitability_overview")

    def test_anonymous_redirects(self, client):
        resp = client.get(self.url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client):
        ProfitabilitySummaryFactory()
        resp = authenticated_client.get(self.url)
        assert resp.status_code == 200
        assert "financials/profitability_overview.html" in [t.name for t in resp.templates]

    def test_context_summaries(self, authenticated_client):
        ProfitabilitySummaryFactory()
        resp = authenticated_client.get(self.url)
        assert "profitability_summaries" in resp.context or "profitabilitysummary_list" in resp.context
