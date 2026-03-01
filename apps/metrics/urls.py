from django.urls import path

from apps.metrics.views import MetricHistoryView, ProjectMetricsView, SCurveDataView

app_name = "metrics"

urlpatterns = [
    path(
        "proyecto/<int:project_pk>/",
        ProjectMetricsView.as_view(),
        name="project_metrics",
    ),
    path(
        "proyecto/<int:project_pk>/scurve/",
        SCurveDataView.as_view(),
        name="scurve_data",
    ),
    path(
        "proyecto/<int:project_pk>/historial/",
        MetricHistoryView.as_view(),
        name="metric_history",
    ),
]
