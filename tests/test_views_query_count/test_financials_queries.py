import pytest
from django.urls import reverse

from tests.factories import PaymentMilestoneFactory, ProfitabilitySummaryFactory

pytestmark = pytest.mark.django_db


class TestFinancialQueryCounts:
    def test_payment_list_query_count(self, django_assert_max_num_queries, authenticated_client, seeded_projects):
        project = seeded_projects[0]
        for _ in range(5):
            PaymentMilestoneFactory(project=project)
        url = reverse("financials:payment_list", kwargs={"project_pk": project.pk})
        with django_assert_max_num_queries(5):
            resp = authenticated_client.get(url)
        assert resp.status_code == 200

    def test_profitability_overview_query_count(self, django_assert_max_num_queries, authenticated_client, seeded_projects):
        for proj in seeded_projects:
            ProfitabilitySummaryFactory(project=proj)
        url = reverse("financials:profitability_overview")
        with django_assert_max_num_queries(15):
            resp = authenticated_client.get(url)
        assert resp.status_code == 200
