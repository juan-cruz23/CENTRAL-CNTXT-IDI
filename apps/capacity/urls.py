from django.urls import path

from apps.capacity.views import (
    AllocationCreateView,
    AllocationMatrixView,
    CapacityAlertListView,
    CapacityHeatmapView,
    CapacityOverviewView,
)

app_name = "capacity"

urlpatterns = [
    path("", CapacityOverviewView.as_view(), name="overview"),
    path("heatmap/", CapacityHeatmapView.as_view(), name="heatmap"),
    path("matriz/", AllocationMatrixView.as_view(), name="matrix"),
    path("alertas/", CapacityAlertListView.as_view(), name="alerts"),
    path("asignar/", AllocationCreateView.as_view(), name="allocate"),
]
