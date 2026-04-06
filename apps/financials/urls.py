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
        "proyecto/<int:project_pk>/pagos/<int:pk>/eliminar/",
        views.PaymentMilestoneDeleteView.as_view(),
        name="payment_delete",
    ),
    path(
        "rentabilidad/",
        views.ProfitabilityOverviewView.as_view(),
        name="profitability_overview",
    ),
    path(
        "rentabilidad-real/",
        views.RealProfitabilityView.as_view(),
        name="real_profitability",
    ),
    path(
        "rentabilidad-real/recalcular/",
        views.RecalculateCostsView.as_view(),
        name="recalculate_costs",
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
    # Maestros — Tipos de gasto operacional
    path("maestros/tipos-gasto/", views.ExpenseTypeListView.as_view(), name="expense_type_list"),
    path("maestros/tipos-gasto/crear/", views.ExpenseTypeCreateView.as_view(), name="expense_type_create"),
    path("maestros/tipos-gasto/<int:pk>/editar/", views.ExpenseTypeUpdateView.as_view(), name="expense_type_update"),
    path("maestros/tipos-gasto/<int:pk>/eliminar/", views.ExpenseTypeDeleteView.as_view(), name="expense_type_delete"),
    # Maestros — Festivos colombianos
    path(
        "maestros/festivos/",
        views.HolidayListView.as_view(),
        name="holiday_list",
    ),
    path(
        "maestros/festivos/crear/",
        views.HolidayCreateView.as_view(),
        name="holiday_create",
    ),
    path(
        "maestros/festivos/<int:pk>/editar/",
        views.HolidayUpdateView.as_view(),
        name="holiday_update",
    ),
    path(
        "maestros/festivos/<int:pk>/eliminar/",
        views.HolidayDeleteView.as_view(),
        name="holiday_delete",
    ),
]
