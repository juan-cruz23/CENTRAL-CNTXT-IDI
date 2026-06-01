from django.contrib import admin
from .models import WeeklyTeam, WeeklyTeamMember


class WeeklyTeamMemberInline(admin.TabularInline):
    model = WeeklyTeamMember
    extra = 1
    fields = ("user", "occupation", "order")


@admin.register(WeeklyTeam)
class WeeklyTeamAdmin(admin.ModelAdmin):
    list_display = ("project_name", "week_number", "year", "created_by", "created_at")
    list_filter = ("year", "week_number")
    search_fields = ("project_name",)
    inlines = [WeeklyTeamMemberInline]
