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
    # Service create / delete (Bloque 2)
    path(
        "<int:pk>/fases/<int:phase_pk>/servicios/crear/",
        views.ServiceInstanceCreateView.as_view(),
        name="service_create",
    ),
    path(
        "<int:pk>/servicios/<int:si_pk>/eliminar/",
        views.ServiceInstanceDeleteView.as_view(),
        name="service_delete",
    ),
    # Prerequisites (HTMX)
    path(
        "<int:pk>/prerequisitos/crear/",
        views.PrerequisiteCreateView.as_view(),
        name="prerequisite_create",
    ),
    path(
        "<int:pk>/prerequisitos/<int:prereq_pk>/toggle/",
        views.PrerequisiteToggleView.as_view(),
        name="prerequisite_toggle",
    ),
    path(
        "<int:pk>/prerequisitos/<int:prereq_pk>/eliminar/",
        views.PrerequisiteDeleteView.as_view(),
        name="prerequisite_delete",
    ),
    # Milestones (HTMX) - Bloque 1
    path(
        "<int:pk>/hitos/crear/",
        views.MilestoneCreateView.as_view(),
        name="milestone_create",
    ),
    path(
        "<int:pk>/hitos/<int:milestone_pk>/eliminar/",
        views.MilestoneDeleteView.as_view(),
        name="milestone_delete",
    ),
    # Validation (HTMX)
    path(
        "<int:pk>/validar-asignacion/",
        views.ValidateAssignmentView.as_view(),
        name="validate_assignment",
    ),
    # Scopes (HTMX)
    path(
        "<int:pk>/alcances/crear/",
        views.ScopeCreateView.as_view(),
        name="scope_create",
    ),
    path(
        "<int:pk>/alcances/<int:scope_pk>/editar/",
        views.ScopeEditView.as_view(),
        name="scope_edit",
    ),
    path(
        "<int:pk>/alcances/<int:scope_pk>/cancelar/",
        views.ScopeCancelEditView.as_view(),
        name="scope_cancel_edit",
    ),
    path(
        "<int:pk>/alcances/<int:scope_pk>/eliminar/",
        views.ScopeDeleteView.as_view(),
        name="scope_delete",
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
