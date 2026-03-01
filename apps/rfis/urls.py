from django.urls import path

from apps.rfis import views

app_name = "rfis"

urlpatterns = [
    path(
        "proyecto/<int:project_pk>/",
        views.RFIListView.as_view(),
        name="rfi_list",
    ),
    path(
        "proyecto/<int:project_pk>/crear/",
        views.RFICreateView.as_view(),
        name="rfi_create",
    ),
    path(
        "proyecto/<int:project_pk>/<int:pk>/",
        views.RFIDetailView.as_view(),
        name="rfi_detail",
    ),
    path(
        "proyecto/<int:project_pk>/<int:pk>/editar/",
        views.RFIUpdateView.as_view(),
        name="rfi_update",
    ),
]
