from django.urls import path

from apps.terceros import views

app_name = "terceros"

urlpatterns = [
    path("", views.ThirdPartyListView.as_view(), name="list"),
    path("<int:pk>/", views.ThirdPartyDetailView.as_view(), name="detail"),
    path("crear/", views.ThirdPartyCreateView.as_view(), name="create"),
    path("<int:pk>/editar/", views.ThirdPartyUpdateView.as_view(), name="update"),
]
