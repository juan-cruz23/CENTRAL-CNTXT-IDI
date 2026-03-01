import pytest
from django.urls import reverse

from tests.factories import AlertFactory, UserFactory


# ---------------------------------------------------------------------------
# AlertListView
# ---------------------------------------------------------------------------
class TestAlertListView:
    url = reverse("notifications:list")

    def test_anonymous_redirects(self, client):
        resp = client.get(self.url)
        assert resp.status_code == 302

    def test_authenticated_get(self, authenticated_client, user):
        alert = AlertFactory()
        alert.target_users.add(user)
        resp = authenticated_client.get(self.url)
        assert resp.status_code == 200
        assert "notifications/list.html" in [t.name for t in resp.templates]

    def test_context_keys(self, authenticated_client, user):
        alert = AlertFactory()
        alert.target_users.add(user)
        resp = authenticated_client.get(self.url)
        ctx = resp.context
        for key in ("alerts", "severity_choices", "category_choices",
                     "current_severity", "current_category", "current_is_read"):
            assert key in ctx

    def test_shows_only_user_alerts(self, authenticated_client, user):
        a1 = AlertFactory()
        a1.target_users.add(user)
        a2 = AlertFactory()
        other_user = UserFactory()
        a2.target_users.add(other_user)
        resp = authenticated_client.get(self.url)
        alerts = list(resp.context["alerts"])
        assert all(user in a.target_users.all() for a in alerts)

    def test_filter_by_severity(self, authenticated_client, user):
        a1 = AlertFactory(severity="WARNING")
        a1.target_users.add(user)
        a2 = AlertFactory(severity="CRITICAL")
        a2.target_users.add(user)
        resp = authenticated_client.get(self.url + "?severity=WARNING")
        alerts = list(resp.context["alerts"])
        assert all(a.severity == "WARNING" for a in alerts)

    def test_filter_by_category(self, authenticated_client, user):
        a1 = AlertFactory(category="COST_OVERRUN")
        a1.target_users.add(user)
        a2 = AlertFactory(category="SCHEDULE_DEVIATION")
        a2.target_users.add(user)
        resp = authenticated_client.get(self.url + "?category=COST_OVERRUN")
        alerts = list(resp.context["alerts"])
        assert all(a.category == "COST_OVERRUN" for a in alerts)

    def test_filter_by_read_status(self, authenticated_client, user):
        a1 = AlertFactory(is_read=False)
        a1.target_users.add(user)
        a2 = AlertFactory(is_read=True)
        a2.target_users.add(user)
        resp = authenticated_client.get(self.url + "?is_read=false")
        alerts = list(resp.context["alerts"])
        assert all(not a.is_read for a in alerts)

    def test_empty_list(self, authenticated_client):
        resp = authenticated_client.get(self.url)
        assert resp.status_code == 200
        alerts = list(resp.context["alerts"])
        assert len(alerts) == 0


# ---------------------------------------------------------------------------
# mark_as_read
# ---------------------------------------------------------------------------
class TestMarkAsRead:
    def test_anonymous_redirects(self, client, db):
        alert = AlertFactory()
        url = reverse("notifications:mark_read", kwargs={"pk": alert.pk})
        resp = client.post(url)
        assert resp.status_code == 302

    def test_get_not_allowed(self, authenticated_client, user):
        alert = AlertFactory()
        alert.target_users.add(user)
        url = reverse("notifications:mark_read", kwargs={"pk": alert.pk})
        resp = authenticated_client.get(url)
        assert resp.status_code == 405

    def test_post_marks_read(self, authenticated_client, user):
        alert = AlertFactory(is_read=False)
        alert.target_users.add(user)
        url = reverse("notifications:mark_read", kwargs={"pk": alert.pk})
        resp = authenticated_client.post(url)
        assert resp.status_code == 204
        alert.refresh_from_db()
        assert alert.is_read is True

    def test_htmx_returns_html(self, authenticated_client, user):
        alert = AlertFactory(is_read=False)
        alert.target_users.add(user)
        url = reverse("notifications:mark_read", kwargs={"pk": alert.pk})
        resp = authenticated_client.post(url, HTTP_HX_REQUEST="true")
        assert resp.status_code == 200
        assert "Leída" in resp.content.decode()


# ---------------------------------------------------------------------------
# mark_as_resolved
# ---------------------------------------------------------------------------
class TestMarkAsResolved:
    def test_anonymous_redirects(self, client, db):
        alert = AlertFactory()
        url = reverse("notifications:mark_resolved", kwargs={"pk": alert.pk})
        resp = client.post(url)
        assert resp.status_code == 302

    def test_get_not_allowed(self, authenticated_client, user):
        alert = AlertFactory()
        alert.target_users.add(user)
        url = reverse("notifications:mark_resolved", kwargs={"pk": alert.pk})
        resp = authenticated_client.get(url)
        assert resp.status_code == 405

    def test_post_marks_resolved(self, authenticated_client, user):
        alert = AlertFactory(is_resolved=False)
        alert.target_users.add(user)
        url = reverse("notifications:mark_resolved", kwargs={"pk": alert.pk})
        resp = authenticated_client.post(url)
        assert resp.status_code == 204
        alert.refresh_from_db()
        assert alert.is_resolved is True
        assert alert.resolved_by == user
        assert alert.resolved_at is not None

    def test_htmx_returns_html(self, authenticated_client, user):
        alert = AlertFactory(is_resolved=False)
        alert.target_users.add(user)
        url = reverse("notifications:mark_resolved", kwargs={"pk": alert.pk})
        resp = authenticated_client.post(url, HTTP_HX_REQUEST="true")
        assert resp.status_code == 200
        assert "Resuelta" in resp.content.decode()
