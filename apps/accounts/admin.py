from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.accounts.models import Role, User, UserRole


class UserRoleInline(admin.TabularInline):
    model = UserRole
    extra = 1


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [UserRoleInline]
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_active_contractor",
        "is_staff",
    )
    list_filter = BaseUserAdmin.list_filter + ("is_active_contractor",)
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Información adicional",
            {
                "fields": (
                    "phone",
                    "avatar",
                    "is_active_contractor",
                    "hourly_rate",
                    "hourly_overhead",
                ),
            },
        ),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            "Información adicional",
            {
                "fields": (
                    "phone",
                    "is_active_contractor",
                    "hourly_rate",
                    "hourly_overhead",
                ),
            },
        ),
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "default_hourly_rate")
    search_fields = ("code", "name")
    list_filter = ("code",)


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "is_primary")
    list_filter = ("role", "is_primary")
    search_fields = ("user__username", "user__first_name", "user__last_name", "role__name")
    autocomplete_fields = ("user", "role")
