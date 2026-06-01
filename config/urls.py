"""
Central Contexto 2.0 - Root URL configuration.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

urlpatterns = [
    # -----------------------------------------------------------------------
    # Admin
    # -----------------------------------------------------------------------
    path("admin/", admin.site.urls),
    # -----------------------------------------------------------------------
    # Authentication (built-in views)
    # -----------------------------------------------------------------------
    path(
        "cuentas/login/",
        auth_views.LoginView.as_view(template_name="accounts/login.html"),
        name="login",
    ),
    path(
        "cuentas/logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),
    # -----------------------------------------------------------------------
    # App URLs
    # -----------------------------------------------------------------------
    path("", include("apps.dashboards.urls", namespace="dashboards")),
    path("cuentas/", include("apps.accounts.urls", namespace="accounts")),
    path("proyectos/", include("apps.projects.urls", namespace="projects")),
    path("servicios/", include("apps.services.urls", namespace="services")),
    path("financiero/", include("apps.financials.urls", namespace="financials")),
    path("metricas/", include("apps.metrics.urls", namespace="metrics")),
    path("capacidad/", include("apps.capacity.urls", namespace="capacity")),
    path("satisfaccion/", include("apps.satisfaction.urls", namespace="satisfaction")),
    path("documentos/", include("apps.documents.urls", namespace="documents")),
    path("rfis/", include("apps.rfis.urls", namespace="rfis")),
    path("importar/", include("apps.imports.urls", namespace="imports")),
    path("notificaciones/", include("apps.notifications.urls", namespace="notifications")),
    path("organizacion/", include("apps.organizations.urls", namespace="organizations")),
    path("terceros/", include("apps.terceros.urls", namespace="terceros")),
    path("tiempos/", include("apps.timetracking.urls", namespace="timetracking")),
    path("calendario/", include("apps.calendar_sync.urls", namespace="calendar_sync")),
    path("herramientas/maestros/", include("apps.geography.urls", namespace="geography")),
    path("equipos/", include("apps.teams.urls", namespace="teams")),
    # -----------------------------------------------------------------------
    # REST API
    # -----------------------------------------------------------------------
    path("api/", include("apps.dashboards.api_urls", namespace="api-dashboards")),
    path("api/cuentas/", include("apps.accounts.api_urls", namespace="api-accounts")),
    path("api/proyectos/", include("apps.projects.api_urls", namespace="api-projects")),
    path("api/servicios/", include("apps.services.api_urls", namespace="api-services")),
    path("api/financiero/", include("apps.financials.api_urls", namespace="api-financials")),
    path("api/metricas/", include("apps.metrics.api_urls", namespace="api-metrics")),
    path("api/capacidad/", include("apps.capacity.api_urls", namespace="api-capacity")),
    path("api/satisfaccion/", include("apps.satisfaction.api_urls", namespace="api-satisfaction")),
    path("api/documentos/", include("apps.documents.api_urls", namespace="api-documents")),
    path("api/rfis/", include("apps.rfis.api_urls", namespace="api-rfis")),
    path("api/importar/", include("apps.imports.api_urls", namespace="api-imports")),
    path("api/notificaciones/", include("apps.notifications.api_urls", namespace="api-notifications")),
    path("api/organizacion/", include("apps.organizations.api_urls", namespace="api-organizations")),
    path("api/tiempos/", include("apps.timetracking.api_urls", namespace="api-timetracking")),
    path("api/calendario/", include("apps.calendar_sync.api_urls", namespace="api-calendar_sync")),
]

# ---------------------------------------------------------------------------
# Debug toolbar & static / media serving in development
# ---------------------------------------------------------------------------
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    try:
        import debug_toolbar  # noqa: F401

        urlpatterns = [
            path("__debug__/", include("debug_toolbar.urls")),
        ] + urlpatterns
    except ImportError:
        pass
