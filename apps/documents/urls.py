from django.urls import path

from apps.documents import views

app_name = "documents"

urlpatterns = [
    path(
        "proyecto/<int:project_pk>/",
        views.ProjectDocumentListView.as_view(),
        name="document_list",
    ),
    path(
        "proyecto/<int:project_pk>/crear/",
        views.ProjectDocumentCreateView.as_view(),
        name="document_create",
    ),
    path(
        "proyecto/<int:project_pk>/<int:pk>/editar/",
        views.ProjectDocumentUpdateView.as_view(),
        name="document_update",
    ),
]
