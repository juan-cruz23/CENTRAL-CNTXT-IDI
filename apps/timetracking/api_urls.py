from django.urls import path
from apps.timetracking.views import time_distribution_summary_api

app_name = "timetracking"

urlpatterns = [
    path("resumen/", time_distribution_summary_api, name="summary_api"),
]
