from django.contrib import admin

from apps.geography.models import Country, Municipality


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ["name", "iso_code", "is_active"]
    search_fields = ["name", "iso_code"]


@admin.register(Municipality)
class MunicipalityAdmin(admin.ModelAdmin):
    list_display = ["name", "department", "country", "is_active"]
    list_filter = ["country", "department"]
    search_fields = ["name", "department"]
