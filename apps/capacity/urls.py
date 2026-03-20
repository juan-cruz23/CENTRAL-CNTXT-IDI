from django.urls import path

from apps.capacity.views import (
    AllocationCreateView,
    AllocationMatrixView,
    CapacityAlertListView,
    CapacityHeatmapView,
    CapacityOverviewView,
    HeatmapDrilldownView,
    ProjectTeamView,
    ServiceInstanceOptionsView,
    ValidateAllocationView,
)

app_name = "capacity"

urlpatterns = [
    path("", CapacityOverviewView.as_view(), name="overview"),
    path("heatmap/", CapacityHeatmapView.as_view(), name="heatmap"),
    path("heatmap/detalle/", HeatmapDrilldownView.as_view(), name="heatmap_drilldown"),
    path("matriz/", AllocationMatrixView.as_view(), name="matrix"),
    path("alertas/", CapacityAlertListView.as_view(), name="alerts"),
    path("asignar/", AllocationCreateView.as_view(), name="allocate"),
    path("servicios-opciones/", ServiceInstanceOptionsView.as_view(), name="service_instance_options"),
    path("validar-asignacion/", ValidateAllocationView.as_view(), name="validate_allocation"),
    path("proyecto/<int:project_pk>/equipo/", ProjectTeamView.as_view(), name="project_team"),
]
