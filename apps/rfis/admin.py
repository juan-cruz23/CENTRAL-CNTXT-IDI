from django.contrib import admin

from apps.rfis.models import RFI


@admin.register(RFI)
class RFIAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "project",
        "service_instance",
        "professional",
        "status",
        "time_invested_hours",
        "created_at",
    )
    list_filter = ("status", "project")
    search_fields = ("code", "observations", "response", "external_discipline")
