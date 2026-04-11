from django.contrib import admin

from apps.services.models import (
    Deliverable,
    ProjectCategory,
    ProjectPhase,
    ServiceActivity,
    ServiceTemplate,
)


class ServiceActivityInline(admin.TabularInline):
    model = ServiceActivity
    extra = 1
    fields = ("order", "name", "responsible_role", "estimated_hours", "description")


class DeliverableInline(admin.TabularInline):
    model = Deliverable
    extra = 1
    fields = ("order", "name", "unit")


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("code", "name", "description")


@admin.register(ProjectPhase)
class ProjectPhaseAdmin(admin.ModelAdmin):
    list_display = ("number", "name")
    search_fields = ("name", "description")


@admin.register(ServiceTemplate)
class ServiceTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "category",
        "phase",
        "base_unit_price",
        "estimated_hours",
        "target_margin_pct",
        "is_active",
    )
    list_filter = ("is_active", "category", "phase")
    search_fields = ("code", "name", "description")
    inlines = [ServiceActivityInline, DeliverableInline]


@admin.register(ServiceActivity)
class ServiceActivityAdmin(admin.ModelAdmin):
    list_display = (
        "service_template",
        "order",
        "name",
        "responsible_role",
        "estimated_hours",
    )
    list_filter = ("service_template__category", "responsible_role")
    search_fields = ("name", "description", "service_template__code")
