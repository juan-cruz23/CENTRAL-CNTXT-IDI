import pytest
from django.urls import reverse
from django.test.utils import override_settings


pytestmark = pytest.mark.django_db


class TestDashboardQueryCounts:
    def test_home_query_count(self, django_assert_max_num_queries, authenticated_client, seeded_projects):
        url = reverse("dashboards:home")
        with django_assert_max_num_queries(15):
            resp = authenticated_client.get(url)
        assert resp.status_code == 200

    def test_portfolio_query_count(self, django_assert_max_num_queries, authenticated_client, seeded_projects):
        url = reverse("dashboards:portfolio")
        with django_assert_max_num_queries(5):
            resp = authenticated_client.get(url)
        assert resp.status_code == 200

    def test_project_dashboard_query_count(self, django_assert_max_num_queries, authenticated_client, seeded_projects):
        project = seeded_projects[0]
        url = reverse("dashboards:project", kwargs={"project_pk": project.pk})
        with django_assert_max_num_queries(12):
            resp = authenticated_client.get(url)
        assert resp.status_code == 200

    def test_leader_dashboard_query_count(self, django_assert_max_num_queries, authenticated_client, user, seeded_projects):
        # Make user the leader of some projects
        for proj in seeded_projects[:3]:
            proj.leader = user
            proj.save(update_fields=["leader"])
        url = reverse("dashboards:leader")
        with django_assert_max_num_queries(10):
            resp = authenticated_client.get(url)
        assert resp.status_code == 200

    def test_portfolio_api_query_count(self, django_assert_max_num_queries, authenticated_client, seeded_projects):
        url = reverse("dashboards:portfolio_data")
        with django_assert_max_num_queries(8):
            resp = authenticated_client.get(url)
        assert resp.status_code == 200

    def test_cashflow_api_query_count(self, django_assert_max_num_queries, authenticated_client, seeded_projects):
        project = seeded_projects[0]
        url = reverse("dashboards:cashflow_data", kwargs={"project_pk": project.pk})
        with django_assert_max_num_queries(5):
            resp = authenticated_client.get(url)
        assert resp.status_code == 200
