from django.urls import path

from apps.services import views

app_name = "services"

urlpatterns = [
    path(
        "categories/",
        views.ProjectCategoryListView.as_view(),
        name="category_list",
    ),
    path(
        "phases/",
        views.ProjectPhaseListView.as_view(),
        name="phase_list",
    ),
    path(
        "templates/",
        views.ServiceTemplateListView.as_view(),
        name="servicetemplate_list",
    ),
    path(
        "templates/<int:pk>/",
        views.ServiceTemplateDetailView.as_view(),
        name="servicetemplate_detail",
    ),
    path(
        "templates/create/",
        views.ServiceTemplateCreateView.as_view(),
        name="servicetemplate_create",
    ),
    path(
        "templates/<int:pk>/update/",
        views.ServiceTemplateUpdateView.as_view(),
        name="servicetemplate_update",
    ),
    path(
        "templates/<int:pk>/delete/",
        views.ServiceTemplateDeleteView.as_view(),
        name="servicetemplate_delete",
    ),
]
