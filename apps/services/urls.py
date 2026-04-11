from django.urls import path

from apps.services import views, views_pricing

app_name = "services"

urlpatterns = [
    path(
        "categories/",
        views.ProjectCategoryListView.as_view(),
        name="category_list",
    ),
    path(
        "categories/crear/",
        views.ProjectCategoryCreateView.as_view(),
        name="category_create",
    ),
    path(
        "categories/<int:pk>/editar/",
        views.ProjectCategoryUpdateView.as_view(),
        name="category_update",
    ),
    path(
        "categories/<int:pk>/eliminar/",
        views.ProjectCategoryDeleteView.as_view(),
        name="category_delete",
    ),
    # Hardware
    path("hardware/", views.HardwareListView.as_view(), name="hardware_list"),
    path("hardware/crear/", views.HardwareCreateView.as_view(), name="hardware_create"),
    path("hardware/<int:pk>/editar/", views.HardwareUpdateView.as_view(), name="hardware_update"),
    path("hardware/<int:pk>/eliminar/", views.HardwareDeleteView.as_view(), name="hardware_delete"),
    # Software
    path("software/", views.SoftwareListView.as_view(), name="software_list"),
    path("software/crear/", views.SoftwareCreateView.as_view(), name="software_create"),
    path("software/<int:pk>/editar/", views.SoftwareUpdateView.as_view(), name="software_update"),
    path("software/<int:pk>/eliminar/", views.SoftwareDeleteView.as_view(), name="software_delete"),
    path(
        "subcategories/",
        views.ServiceSubCategoryListView.as_view(),
        name="subcategory_list",
    ),
    path(
        "subcategories/crear/",
        views.ServiceSubCategoryCreateView.as_view(),
        name="subcategory_create",
    ),
    path(
        "subcategories/<int:pk>/editar/",
        views.ServiceSubCategoryUpdateView.as_view(),
        name="subcategory_update",
    ),
    path(
        "subcategories/<int:pk>/eliminar/",
        views.ServiceSubCategoryDeleteView.as_view(),
        name="subcategory_delete",
    ),
    # Entregables
    path("entregables/", views.DeliverableListView.as_view(), name="deliverable_list"),
    path("entregables/crear/", views.DeliverableCreateView.as_view(), name="deliverable_create"),
    path("entregables/<int:pk>/editar/", views.DeliverableUpdateView.as_view(), name="deliverable_update"),
    path("entregables/<int:pk>/eliminar/", views.DeliverableDeleteView.as_view(), name="deliverable_delete"),
    path(
        "phases/",
        views.ProjectPhaseListView.as_view(),
        name="phase_list",
    ),
    path(
        "phases/crear/",
        views.ProjectPhaseCreateView.as_view(),
        name="phase_create",
    ),
    path(
        "phases/<int:pk>/editar/",
        views.ProjectPhaseUpdateView.as_view(),
        name="phase_update",
    ),
    path(
        "phases/<int:pk>/eliminar/",
        views.ProjectPhaseDeleteView.as_view(),
        name="phase_delete",
    ),
    path(
        "templates/",
        views.ServiceTemplateListView.as_view(),
        name="servicetemplate_list",
    ),
    path(
        "templates/<int:pk>/",
        views.ServiceTemplateDetailView.as_view(),
        name="servicetemplate_detail",
    ),
    path(
        "templates/create/",
        views.ServiceTemplateCreateView.as_view(),
        name="servicetemplate_create",
    ),
    path(
        "templates/<int:pk>/update/",
        views.ServiceTemplateUpdateView.as_view(),
        name="servicetemplate_update",
    ),
    path(
        "templates/<int:pk>/delete/",
        views.ServiceTemplateDeleteView.as_view(),
        name="servicetemplate_delete",
    ),
    path(
        "templates/<int:pk>/calcular-dias/",
        views.CalcEstimatedDaysView.as_view(),
        name="servicetemplate_calc_days",
    ),
    path(
        "calcular-horas-dias/",
        views.CalcHoursDaysView.as_view(),
        name="calc_hours_days",
    ),
    path(
        "calcular-pricing/",
        views.CalcPricingView.as_view(),
        name="calc_pricing",
    ),
    # Pricing dashboard
    path(
        "pricing/",
        views.PricingDashboardView.as_view(),
        name="pricing_dashboard",
    ),
    path(
        "pricing/<int:pk>/editar/",
        views.ServiceTemplateInlineEditView.as_view(),
        name="pricing_inline_edit",
    ),
    path(
        "pricing/<int:pk>/cancelar/",
        views.ServiceTemplateInlineCancelView.as_view(),
        name="pricing_inline_cancel",
    ),
    # Pricing change requests
    path(
        "pricing-requests/",
        views_pricing.PricingChangeRequestListView.as_view(),
        name="pricing_request_list",
    ),
    path(
        "pricing-requests/<int:si_pk>/crear/",
        views_pricing.PricingChangeRequestCreateView.as_view(),
        name="pricing_request_create",
    ),
    path(
        "pricing-requests/<int:pk>/revisar/",
        views_pricing.PricingChangeRequestReviewView.as_view(),
        name="pricing_request_review",
    ),
]
