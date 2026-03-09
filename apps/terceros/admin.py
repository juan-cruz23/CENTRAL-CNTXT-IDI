from django.contrib import admin

from apps.terceros.models import ThirdParty, ThirdPartyContact


class ThirdPartyContactInline(admin.TabularInline):
    model = ThirdPartyContact
    extra = 0


@admin.register(ThirdParty)
class ThirdPartyAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "relationship_type", "client_category", "is_active")
    list_filter = ("relationship_type", "client_category", "is_active")
    search_fields = ("name", "company", "nit", "email")
    inlines = [ThirdPartyContactInline]


@admin.register(ThirdPartyContact)
class ThirdPartyContactAdmin(admin.ModelAdmin):
    list_display = ("name", "third_party", "role", "email", "is_primary")
    list_filter = ("is_primary",)
    search_fields = ("name", "email")
