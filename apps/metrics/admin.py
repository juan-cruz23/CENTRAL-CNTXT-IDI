from django.contrib import admin

from apps.metrics.models import ProjectMetricSnapshot


@admin.register(ProjectMetricSnapshot)
class ProjectMetricSnapshotAdmin(admin.ModelAdmin):
    list_display = (
        "project",
        "snapshot_date",
        "bac",
        "planned_value",
        "earned_value",
        "actual_cost",
        "spi",
        "cpi",
        "overall_progress_pct",
        "expected_progress_pct",
        "projected_margin_pct",
    )
    list_filter = (
        "project",
        "snapshot_date",
    )
    search_fields = (
        "project__name",
    )
    date_hierarchy = "snapshot_date"
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (None, {
            "fields": ("project", "snapshot_date"),
        }),
        ("EVM Core", {
            "fields": ("bac", "planned_value", "earned_value", "actual_cost"),
        }),
        ("Performance Indices", {
            "fields": ("spi", "cpi"),
        }),
        ("Variances", {
            "fields": ("schedule_variance", "cost_variance"),
        }),
        ("Forecasts", {
            "fields": ("eac", "etc", "vac"),
        }),
        ("Progress", {
            "fields": ("overall_progress_pct", "expected_progress_pct", "schedule_deviation_pct"),
        }),
        ("Financial", {
            "fields": ("total_revenue", "total_costs", "projected_margin_pct"),
        }),
        ("Auditoría", {
            "fields": ("created_at", "updated_at"),
        }),
    )
