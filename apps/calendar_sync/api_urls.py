from django.urls import path
from apps.calendar_sync.views import CalendarWeeklySummaryAPI

app_name = "calendar_sync"

urlpatterns = [
    path("resumen-semanal/", CalendarWeeklySummaryAPI.as_view(), name="weekly_summary"),
]
