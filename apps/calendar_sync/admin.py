from django.contrib import admin
from apps.calendar_sync.models import (
    CalendarEvent,
    GoogleCalendarConnection,
    ProjectColorMapping,
    ProjectKeywordMapping,
)


@admin.register(GoogleCalendarConnection)
class GoogleCalendarConnectionAdmin(admin.ModelAdmin):
    list_display = ("user", "is_active", "last_sync")
    list_filter = ("is_active",)


@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "start_time", "duration_hours", "project", "match_method")
    list_filter = ("match_method", "is_meeting")
    search_fields = ("title", "user__first_name", "user__last_name")
    raw_id_fields = ("user", "project")


@admin.register(ProjectColorMapping)
class ProjectColorMappingAdmin(admin.ModelAdmin):
    list_display = ("user", "color_id", "color_name", "project")


@admin.register(ProjectKeywordMapping)
class ProjectKeywordMappingAdmin(admin.ModelAdmin):
    list_display = ("project", "keyword")
    search_fields = ("keyword", "project__code", "project__name")
