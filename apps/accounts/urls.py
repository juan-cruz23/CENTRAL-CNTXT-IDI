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
    # Role CRUD (Maestros)
    path("roles/", views.RoleListView.as_view(), name="role_list"),
    path("roles/crear/", views.RoleCreateView.as_view(), name="role_create"),
    path("roles/<int:pk>/editar/", views.RoleUpdateView.as_view(), name="role_update"),
    path("roles/<int:pk>/eliminar/", views.RoleDeleteView.as_view(), name="role_delete"),
    # User creation / update
    path("usuarios/crear/", views.UserCreateView.as_view(), name="user_create"),
    path("usuarios/<int:pk>/creado/", views.UserCreatedView.as_view(), name="user_created"),
    path("usuarios/<int:pk>/editar/", views.UserUpdateView.as_view(), name="user_update"),
    # AccessPackage CRUD
    path("paquetes-acceso/", views.AccessPackageListView.as_view(), name="access_package_list"),
    path("paquetes-acceso/crear/", views.AccessPackageCreateView.as_view(), name="access_package_create"),
    path("paquetes-acceso/<int:pk>/editar/", views.AccessPackageUpdateView.as_view(), name="access_package_update"),
    path("paquetes-acceso/<int:pk>/eliminar/", views.AccessPackageDeleteView.as_view(), name="access_package_delete"),
    # WorkSchedule CRUD
    path("jornadas/", views.WorkScheduleListView.as_view(), name="work_schedule_list"),
    path("jornadas/crear/", views.WorkScheduleCreateView.as_view(), name="work_schedule_create"),
    path("jornadas/<int:pk>/editar/", views.WorkScheduleUpdateView.as_view(), name="work_schedule_update"),
    path("jornadas/<int:pk>/eliminar/", views.WorkScheduleDeleteView.as_view(), name="work_schedule_delete"),
]
