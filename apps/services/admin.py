from django.contrib import admin

from apps.services.models import (
    Deliverable,
    KeyActivity,
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


class KeyActivityInline(admin.TabularInline):
    model = KeyActivity
    extra = 1
    fields = ("order", "name")


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


@admin.register(Deliverable)
class DeliverableAdmin(admin.ModelAdmin):
    list_display = ("service_template", "name", "unit", "order")
    list_filter = ("service_template__category",)
    search_fields = ("name", "service_template__code")
    inlines = [KeyActivityInline]


@admin.register(KeyActivity)
class KeyActivityAdmin(admin.ModelAdmin):
    list_display = ("deliverable", "name", "order")
    search_fields = ("name", "deliverable__name", "deliverable__service_template__code")


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
