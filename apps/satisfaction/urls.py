from django.urls import path

from apps.satisfaction.views import (
    CVECreateView,
    ProjectSatisfactionView,
    PublicSurveyView,
    SurveyCreateView,
)

app_name = "satisfaction"

urlpatterns = [
    path(
        "proyecto/<int:project_pk>/",
        ProjectSatisfactionView.as_view(),
        name="project_satisfaction",
    ),
    path(
        "proyecto/<int:project_pk>/cve/crear/",
        CVECreateView.as_view(),
        name="cve_create",
    ),
    path(
        "proyecto/<int:project_pk>/encuesta/crear/",
        SurveyCreateView.as_view(),
        name="survey_create",
    ),
    path(
        "encuesta/<uuid:token>/",
        PublicSurveyView.as_view(),
        name="public_survey",
    ),
]
