from django.contrib.auth import views as auth_views
from django.urls import path

from apps.accounts import views

app_name = "accounts"

urlpatterns = [
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="accounts/login.html"),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),
    path(
        "profile/",
        views.ProfileView.as_view(),
        name="profile",
    ),
    path(
        "usuarios/",
        views.UserManagementView.as_view(),
        name="user_management",
    ),
    path(
        "usuarios/<int:pk>/roles/",
        views.UserRoleUpdateView.as_view(),
        name="user_role_update",
    ),
]
