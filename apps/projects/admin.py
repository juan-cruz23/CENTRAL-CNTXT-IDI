from django.contrib import admin

from apps.projects.models import (
    Client,
    Milestone,
    PrerequisiteTemplate,
    Project,
    ProjectPhaseInstance,
    ProjectPrerequisite,
    ServiceInstance,
)


# ---------------------------------------------------------------------------
# Inlines
# ---------------------------------------------------------------------------
class ProjectPrerequisiteInline(admin.TabularInline):
    model = ProjectPrerequisite
    extra = 0
    fields = (
        "category",
        "prerequisite_type",
        "name",
        "is_completed",
        "weight_pct",
    )


class MilestoneInline(admin.TabularInline):
    model = Milestone
    extra = 0
    fields = (
        "code",
        "name",
        "milestone_type",
        "phase_instance",
        "planned_date",
        "actual_date",
    )


class ServiceInstanceInline(admin.TabularInline):
    model = ServiceInstance
    extra = 0
    fields = (
        "code",
        "name",
        "quantity",
        "unit_price",
        "total_value",
        "progress_pct",
        "assigned_professional",
    )
    readonly_fields = ("total_value",)
    show_change_link = True


class ProjectPhaseInstanceInline(admin.TabularInline):
    model = ProjectPhaseInstance
    extra = 0
    fields = (
        "phase",
        "order",
        "planned_start_date",
        "planned_end_date",
        "total_value",
        "progress_pct",
    )
    show_change_link = True


# ---------------------------------------------------------------------------
# ModelAdmin classes
# ---------------------------------------------------------------------------
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "category", "email", "phone")
    list_filter = ("category",)
    search_fields = ("name", "company", "email")
    ordering = ("name",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "client",
        "status",
        "leader",
        "current_progress_pct",
        "total_value",
        "planned_start_date",
        "planned_end_date",
    )
    list_filter = (
        "status",
        "access_type",
        "client_category",
        "business_unit",
        "operative_line",
        "country",
    )
    search_fields = ("code", "name", "client__name")
    autocomplete_fields = (
        "client",
        "category",
        "business_unit",
        "operative_line",
        "leader",
    )
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"
    inlines = [
        ProjectPhaseInstanceInline,
        ProjectPrerequisiteInline,
        MilestoneInline,
    ]
    fieldsets = (
        (
            "Identificación",
            {
                "fields": (
                    "code",
                    "name",
                    "client",
                    "category",
                    "client_category",
                    "access_type",
                ),
            },
        ),
        (
            "Ubicación",
            {
                "fields": ("location", "country"),
            },
        ),
        (
            "Organización",
            {
                "fields": (
                    "status",
                    "business_unit",
                    "operative_line",
                    "leader",
                ),
            },
        ),
        (
            "Cronograma",
            {
                "fields": (
                    "planned_start_date",
                    "planned_end_date",
                    "actual_start_date",
                    "actual_end_date",
                ),
            },
        ),
        (
            "Financiero",
            {
                "fields": ("total_value", "iva_rate"),
            },
        ),
        (
            "Métricas",
            {
                "fields": (
                    "current_progress_pct",
                    "schedule_deviation_pct",
                    "profitability_pct",
                    "client_satisfaction_score",
                ),
            },
        ),
        (
            "Notas",
            {
                "fields": ("notes",),
                "classes": ("collapse",),
            },
        ),
        (
            "Auditoría",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(ProjectPrerequisite)
class ProjectPrerequisiteAdmin(admin.ModelAdmin):
    list_display = (
        "project",
        "category",
        "prerequisite_type",
        "name",
        "is_completed",
        "weight_pct",
    )
    list_filter = ("category", "is_completed")
    search_fields = ("name", "prerequisite_type", "project__code", "project__name")
    autocomplete_fields = ("project",)


@admin.register(ProjectPhaseInstance)
class ProjectPhaseInstanceAdmin(admin.ModelAdmin):
    list_display = (
        "project",
        "phase",
        "order",
        "planned_start_date",
        "planned_end_date",
        "total_value",
        "progress_pct",
    )
    list_filter = ("phase",)
    search_fields = ("project__code", "project__name")
    autocomplete_fields = ("project", "phase")
    inlines = [ServiceInstanceInline]


@admin.register(ServiceInstance)
class ServiceInstanceAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "project",
        "phase_instance",
        "quantity",
        "unit_price",
        "total_value",
        "progress_pct",
        "assigned_professional",
    )
    list_filter = (
        "is_checked",
        "is_real_checked",
        "is_milestone",
        "is_review_period",
    )
    search_fields = (
        "code",
        "name",
        "project__code",
        "project__name",
    )
    autocomplete_fields = (
        "project",
        "phase_instance",
        "service_template",
        "responsible_role",
        "assigned_professional",
    )
    readonly_fields = ("total_value", "created_at", "updated_at")
    fieldsets = (
        (
            "Identificación",
            {
                "fields": (
                    "project",
                    "phase_instance",
                    "service_template",
                    "code",
                    "name",
                ),
            },
        ),
        (
            "Financiero",
            {
                "fields": (
                    "quantity",
                    "unit_price",
                    "total_value",
                    "incidence_pct",
                    "deductions",
                    "real_operative_cost",
                    "estimated_operative_cost",
                    "margin_pct",
                ),
            },
        ),
        (
            "Avance",
            {
                "fields": (
                    "is_checked",
                    "progress_pct",
                    "is_real_checked",
                    "expected_progress_pct",
                ),
            },
        ),
        (
            "Asignación",
            {
                "fields": (
                    "responsible_role",
                    "assigned_professional",
                    "support_notes",
                ),
            },
        ),
        (
            "Cronograma",
            {
                "fields": (
                    "projected_hours",
                    "projected_start_date",
                    "actual_start_date",
                    "projected_days",
                    "projected_end_date",
                    "actual_end_date",
                    "actual_hours",
                    "operative_deviation_pct",
                ),
            },
        ),
        (
            "Flags",
            {
                "fields": ("is_milestone", "is_review_period"),
            },
        ),
        (
            "Auditoría",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(PrerequisiteTemplate)
class PrerequisiteTemplateAdmin(admin.ModelAdmin):
    list_display = ("project_category", "category", "prerequisite_type", "name", "weight_pct")
    list_filter = ("project_category", "category")
    search_fields = ("name", "prerequisite_type", "project_category__name")


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "project",
        "milestone_type",
        "phase_instance",
        "planned_date",
        "actual_date",
    )
    list_filter = ("milestone_type",)
    search_fields = ("code", "name", "project__code", "project__name")
    autocomplete_fields = ("project", "phase_instance")
