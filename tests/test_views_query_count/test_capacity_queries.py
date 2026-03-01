import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


class TestCapacityQueryCounts:
    def test_overview_query_count(self, django_assert_max_num_queries, authenticated_client, seeded_projects):
        url = reverse("capacity:overview")
        with django_assert_max_num_queries(20):
            resp = authenticated_client.get(url)
        assert resp.status_code == 200

    def test_matrix_query_count(self, django_assert_max_num_queries, authenticated_client, seeded_projects):
        url = reverse("capacity:matrix")
        with django_assert_max_num_queries(5):
            resp = authenticated_client.get(url)
        assert resp.status_code == 200
