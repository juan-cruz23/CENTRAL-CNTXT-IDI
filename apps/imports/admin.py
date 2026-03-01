from django.contrib import admin

from apps.imports.models import ImportJob


@admin.register(ImportJob)
class ImportJobAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "source_type",
        "status",
        "uploaded_by",
        "records_total",
        "records_imported",
        "records_failed",
        "created_at",
        "completed_at",
    )
    list_filter = ("source_type", "status")
    search_fields = (
        "uploaded_by__username",
        "uploaded_by__first_name",
        "uploaded_by__last_name",
    )
    readonly_fields = (
        "records_total",
        "records_imported",
        "records_failed",
        "errors",
        "completed_at",
    )
    autocomplete_fields = ("uploaded_by",)
