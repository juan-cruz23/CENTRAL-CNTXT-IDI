from django.urls import path

from apps.dashboards.views import (
    ExecutiveDashboardView,
    LeaderDashboardView,
    PortfolioDashboardView,
    ProjectDashboardView,
    SystemDashboardView,
    bu_cashflow_api,
    cashflow_data_api,
    company_cashflow_api,
    gantt_data_api,
    periodic_cashflow_api,
    portfolio_by_bu_api,
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
    path(
        "api/cashflow-periodic/<int:project_pk>/",
        periodic_cashflow_api,
        name="periodic_cashflow",
    ),
    path("api/cashflow-company/", company_cashflow_api, name="company_cashflow"),
    path(
        "api/cashflow-bu/<str:bu_code>/",
        bu_cashflow_api,
        name="bu_cashflow",
    ),
    path("api/gantt-data/", gantt_data_api, name="gantt_data"),
    path("api/portfolio-by-bu/", portfolio_by_bu_api, name="portfolio_by_bu"),
]
