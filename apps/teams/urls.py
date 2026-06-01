from django.urls import path
from .views import TeamManagementView

app_name = "teams"

urlpatterns = [
    path("", TeamManagementView.as_view(), name="list"),
]
