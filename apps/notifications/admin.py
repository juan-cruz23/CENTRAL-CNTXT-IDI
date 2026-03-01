from django.contrib import admin

from apps.notifications.models import Alert


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "project",
        "severity",
        "category",
        "is_read",
        "is_resolved",
        "created_at",
    )
    list_filter = ("severity", "category", "is_read", "is_resolved")
    search_fields = ("title", "message", "project__code", "project__name")
    autocomplete_fields = ("project", "resolved_by")
    filter_horizontal = ("target_users",)
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"
