from django.urls import path

from apps.notifications.views import AlertListView, mark_as_read, mark_as_resolved

app_name = "notifications"

urlpatterns = [
    path("", AlertListView.as_view(), name="list"),
    path("<int:pk>/leer/", mark_as_read, name="mark_read"),
    path("<int:pk>/resolver/", mark_as_resolved, name="mark_resolved"),
]
