from django.urls import path

from apps.dashboards.views import (
    ExecutiveDashboardView,
    LeaderDashboardView,
    PortfolioDashboardView,
    ProjectDashboardView,
    SystemDashboardView,
    cashflow_data_api,
    portfolio_data_api,
)

app_name = "dashboards"

urlpatterns = [
    path("", ExecutiveDashboardView.as_view(), name="home"),
    path("portfolio/", PortfolioDashboardView.as_view(), name="portfolio"),
    path(
        "proyecto/<int:project_pk>/",
        ProjectDashboardView.as_view(),
        name="project",
    ),
    path(
        "sistema/<str:system_code>/",
        SystemDashboardView.as_view(),
        name="system",
    ),
    path("mi-tablero/", LeaderDashboardView.as_view(), name="leader"),
    path("api/portfolio-data/", portfolio_data_api, name="portfolio_data"),
    path(
        "api/cashflow-data/<int:project_pk>/",
        cashflow_data_api,
        name="cashflow_data",
    ),
]
