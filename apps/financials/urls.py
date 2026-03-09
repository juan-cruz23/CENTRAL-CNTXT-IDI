from django.urls import path

from apps.financials import views, views_allocation

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
    # Cost center mapping
    path(
        "centros-costo/",
        views.CostCenterMappingListView.as_view(),
        name="cost_center_mapping",
    ),
    path(
        "centros-costo/<int:pk>/editar/",
        views.CostCenterMappingUpdateView.as_view(),
        name="cost_center_mapping_update",
    ),
    # Accounting overview
    path(
        "contabilidad/",
        views.AccountingOverviewView.as_view(),
        name="accounting_overview",
    ),
    # Cost allocation (prorrateo)
    path(
        "prorrateo/",
        views_allocation.CostAllocationOverviewView.as_view(),
        name="cost_allocation_overview",
    ),
    path(
        "prorrateo/ejecutar/",
        views_allocation.CostAllocationRunView.as_view(),
        name="cost_allocation_run",
    ),
    path(
        "prorrateo/<int:pk>/",
        views_allocation.CostAllocationDetailView.as_view(),
        name="cost_allocation_detail",
    ),
]
