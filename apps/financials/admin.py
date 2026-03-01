from django.contrib import admin

from apps.financials.models import (
    ColombianHoliday,
    PaymentMilestone,
    ProfitabilitySummary,
)


@admin.register(PaymentMilestone)
class PaymentMilestoneAdmin(admin.ModelAdmin):
    list_display = (
        "project",
        "concept",
        "proposed_value",
        "iva_value",
        "incidence_pct",
        "status",
        "executed_value",
        "difference",
        "billing_date",
    )
    list_filter = ("status", "project")
    search_fields = ("concept", "invoice_number", "notes")


@admin.register(ProfitabilitySummary)
class ProfitabilitySummaryAdmin(admin.ModelAdmin):
    list_display = (
        "project",
        "milestone_name",
        "value",
        "revenue",
        "utility",
        "margin_pct",
        "is_verified",
    )
    list_filter = ("is_verified", "project")
    search_fields = ("milestone_name",)


@admin.register(ColombianHoliday)
class ColombianHolidayAdmin(admin.ModelAdmin):
    list_display = ("date", "name")
    search_fields = ("name",)
    list_filter = ("date",)
