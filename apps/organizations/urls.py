from django.urls import path

from apps.organizations import views

app_name = "organizations"

urlpatterns = [
    path(
        "systems/",
        views.OrganizationalSystemListView.as_view(),
        name="system_list",
    ),
    path(
        "business-units/",
        views.BusinessUnitListView.as_view(),
        name="businessunit_list",
    ),
    path(
        "operative-lines/",
        views.OperativeLineListView.as_view(),
        name="operativeline_list",
    ),
]
