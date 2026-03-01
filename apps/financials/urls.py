from django.urls import path

from apps.financials import views

app_name = "financials"

urlpatterns = [
    path(
        "proyecto/<int:project_pk>/",
        views.ProjectFinancialView.as_view(),
        name="project_financial",
    ),
    path(
        "proyecto/<int:project_pk>/pagos/",
        views.PaymentMilestoneListView.as_view(),
        name="payment_list",
    ),
    path(
        "proyecto/<int:project_pk>/pagos/crear/",
        views.PaymentMilestoneCreateView.as_view(),
        name="payment_create",
    ),
    path(
        "proyecto/<int:project_pk>/pagos/<int:pk>/editar/",
        views.PaymentMilestoneUpdateView.as_view(),
        name="payment_update",
    ),
    path(
        "rentabilidad/",
        views.ProfitabilityOverviewView.as_view(),
        name="profitability_overview",
    ),
]
