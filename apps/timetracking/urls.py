from django.urls import path
from apps.timetracking import views

app_name = "timetracking"

urlpatterns = [
    path("", views.TimeDistributionWidgetView.as_view(), name="widget"),
    path("historial/", views.TimeDistributionHistoryView.as_view(), name="history"),
    path("<int:pk>/editar/", views.TimeDistributionEditView.as_view(), name="edit"),
    path("guardar/", views.TimeDistributionSaveView.as_view(), name="save"),
    path("enviar/", views.TimeDistributionSubmitView.as_view(), name="submit"),
    path("api/resumen/", views.time_distribution_summary_api, name="summary_api"),
]
