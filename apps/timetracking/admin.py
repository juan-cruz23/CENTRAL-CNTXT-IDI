from django.contrib import admin
from apps.timetracking.models import WeeklyTimeDistribution, TimeDistributionEntry


class TimeDistributionEntryInline(admin.TabularInline):
    model = TimeDistributionEntry
    extra = 0


@admin.register(WeeklyTimeDistribution)
class WeeklyTimeDistributionAdmin(admin.ModelAdmin):
    list_display = ("user", "week_start", "status", "submitted_at")
    list_filter = ("status", "week_start")
    search_fields = ("user__first_name", "user__last_name")
    inlines = [TimeDistributionEntryInline]
