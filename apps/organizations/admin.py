from django.contrib import admin

from apps.organizations.models import BusinessUnit, OperativeLine, OrganizationalSystem


@admin.register(OrganizationalSystem)
class OrganizationalSystemAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "analogy", "leader", "is_active")
    list_filter = ("is_active", "code")
    search_fields = ("code", "name", "analogy", "description")


@admin.register(BusinessUnit)
class BusinessUnitAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "leader", "is_active")
    list_filter = ("is_active", "code")
    search_fields = ("code", "name", "description")


@admin.register(OperativeLine)
class OperativeLineAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "business_unit", "is_active")
    list_filter = ("is_active", "business_unit")
    search_fields = ("code", "name", "description")
