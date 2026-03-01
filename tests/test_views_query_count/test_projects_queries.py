import pytest
from django.urls import reverse

from tests.factories import ClientFactory

pytestmark = pytest.mark.django_db


class TestProjectQueryCounts:
    def test_project_list_query_count(self, django_assert_max_num_queries, authenticated_client, seeded_projects):
        url = reverse("projects:list")
        with django_assert_max_num_queries(5):
            resp = authenticated_client.get(url)
        assert resp.status_code == 200

    def test_project_detail_query_count(self, django_assert_max_num_queries, authenticated_client, seeded_projects):
        project = seeded_projects[0]
        url = reverse("projects:detail", kwargs={"pk": project.pk})
        with django_assert_max_num_queries(10):
            resp = authenticated_client.get(url)
        assert resp.status_code == 200

    def test_client_list_query_count(self, django_assert_max_num_queries, authenticated_client, seeded_projects):
        for _ in range(10):
            ClientFactory()
        url = reverse("projects:client_list")
        with django_assert_max_num_queries(25):
            resp = authenticated_client.get(url)
        assert resp.status_code == 200

    def test_project_list_with_filters_query_count(self, django_assert_max_num_queries, authenticated_client, seeded_projects):
        url = reverse("projects:list") + "?status=ACTIVE&q=test"
        with django_assert_max_num_queries(5):
            resp = authenticated_client.get(url)
        assert resp.status_code == 200
