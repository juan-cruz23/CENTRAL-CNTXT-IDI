import pytest
from django.urls import reverse


class TestProfileView:
    url = reverse("accounts:profile")

    def test_anonymous_redirects(self, client):
        resp = client.get(self.url)
        assert resp.status_code == 302
        assert "/cuentas/login/" in resp.url

    def test_authenticated_get(self, authenticated_client):
        resp = authenticated_client.get(self.url)
        assert resp.status_code == 200
        assert "accounts/profile.html" in [t.name for t in resp.templates]

    def test_context_user_roles(self, authenticated_client):
        resp = authenticated_client.get(self.url)
        assert "user_roles" in resp.context


class TestLoginRedirect:
    def test_login_page_loads(self, client):
        url = reverse("login")
        resp = client.get(url)
        assert resp.status_code == 200
