from django.contrib import admin

from apps.capacity.models import CapacityAlert, ProjectAllocation, TeamMemberCapacity


@admin.register(TeamMemberCapacity)
class TeamMemberCapacityAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "weekly_available_hours",
        "effective_from",
        "effective_until",
    )
    list_filter = ("effective_from",)
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
    )
    autocomplete_fields = ("user",)


@admin.register(ProjectAllocation)
class ProjectAllocationAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "project",
        "role",
        "start_date",
        "end_date",
        "weekly_hours",
        "allocation_pct",
    )
    list_filter = ("start_date", "role")
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "project__code",
        "project__name",
    )
    autocomplete_fields = ("user", "project", "role")


@admin.register(CapacityAlert)
class CapacityAlertAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "alert_type",
        "week_start",
        "allocated_hours",
        "available_hours",
        "is_resolved",
    )
    list_filter = ("alert_type", "is_resolved")
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
    )
    autocomplete_fields = ("user",)
