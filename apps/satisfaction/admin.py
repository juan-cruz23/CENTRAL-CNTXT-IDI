from django.contrib import admin

from apps.satisfaction.models import SatisfactionMeasurement, SatisfactionSurvey


class SatisfactionSurveyInline(admin.StackedInline):
    model = SatisfactionSurvey
    extra = 0
    fields = (
        "general_sensation",
        "clarity_and_support",
        "personal_effort",
        "team_relationship",
        "confidence",
        "perceived_value",
        "total_score_pct",
        "notes",
    )
    readonly_fields = ("total_score_pct",)


@admin.register(SatisfactionMeasurement)
class SatisfactionMeasurementAdmin(admin.ModelAdmin):
    list_display = (
        "project",
        "milestone",
        "measurement_date",
        "observed_emotion_pct",
        "spontaneous_phrase_pct",
        "symbolic_object_pct",
        "cve_score",
    )
    list_filter = ("measurement_date",)
    search_fields = (
        "project__code",
        "project__name",
    )
    autocomplete_fields = ("project", "milestone")
    readonly_fields = ("cve_score",)
    inlines = [SatisfactionSurveyInline]


@admin.register(SatisfactionSurvey)
class SatisfactionSurveyAdmin(admin.ModelAdmin):
    list_display = (
        "measurement",
        "general_sensation",
        "clarity_and_support",
        "personal_effort",
        "team_relationship",
        "confidence",
        "perceived_value",
        "total_score_pct",
    )
    search_fields = (
        "measurement__project__code",
        "measurement__project__name",
    )
    readonly_fields = ("total_score_pct",)
