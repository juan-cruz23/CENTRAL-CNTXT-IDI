from django.urls import path

from apps.projects import views

app_name = "projects"

urlpatterns = [
    # Projects
    path(
        "",
        views.ProjectListView.as_view(),
        name="list",
    ),
    path(
        "<int:pk>/",
        views.ProjectDetailView.as_view(),
        name="detail",
    ),
    path(
        "crear/",
        views.ProjectCreateView.as_view(),
        name="create",
    ),
    path(
        "<int:pk>/editar/",
        views.ProjectUpdateView.as_view(),
        name="update",
    ),
    # Phase services
    path(
        "<int:pk>/fases/<int:phase_pk>/servicios/",
        views.ServiceInstanceListView.as_view(),
        name="phase_services",
    ),
    path(
        "<int:pk>/servicios/<int:si_pk>/editar/",
        views.ServiceInstanceUpdateView.as_view(),
        name="service_update",
    ),
    # Clients
    path(
        "clientes/",
        views.ClientListView.as_view(),
        name="client_list",
    ),
    path(
        "clientes/crear/",
        views.ClientCreateView.as_view(),
        name="client_create",
    ),
]
