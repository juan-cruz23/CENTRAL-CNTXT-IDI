from django.contrib.auth.mixins import AccessMixin
from django.http import HttpResponseForbidden

from apps.common.models import AuditLog


# ---------------------------------------------------------------------------
# Role-based access control
# ---------------------------------------------------------------------------

# Roles that can see financial data (rentabilidad, contabilidad, prorrateo)
FINANCIAL_ROLES = {"DO", "LA"}

# Roles that can edit pricing/service values
PRICING_EDIT_ROLES = {"DO"}

# Roles that can see the executive dashboard with strategic data
EXECUTIVE_ROLES = {"DO", "LA", "LP", "DM"}

# Roles with full operational access (capacity, heatmap, etc.)
OPERATIONAL_ROLES = {"DO", "LA", "LP", "DM", "INT"}


def get_user_role_codes(user):
    """Returns a set of role codes assigned to the user."""
    if not user.is_authenticated:
        return set()
    return set(user.user_roles.values_list("role__code", flat=True))


def user_has_any_role(user, role_codes):
    """Check if user has any of the given role codes."""
    if user.is_staff:
        return True
    return bool(get_user_role_codes(user) & set(role_codes))


def user_can_view_financials(user):
    """Can the user see financial data?"""
    return user_has_any_role(user, FINANCIAL_ROLES)


def user_can_edit_pricing(user):
    """Can the user edit pricing/service template values?"""
    return user_has_any_role(user, PRICING_EDIT_ROLES)


def user_can_view_executive(user):
    """Can the user see executive/strategic dashboards?"""
    return user_has_any_role(user, EXECUTIVE_ROLES)


def user_can_view_operations(user):
    """Can the user see operational views?"""
    return user_has_any_role(user, OPERATIONAL_ROLES)


class RoleFlagRequiredMixin(AccessMixin):
    """
    Mixin that requires the user to have a specific boolean flag set on at least
    one of their roles (or be staff).

    Usage:
        class MyView(RoleFlagRequiredMixin, CreateView):
            required_role_flag = "can_create_projects"
    """

    required_role_flag: str = ""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not _user_has_role_flag(request.user, self.required_role_flag):
            return HttpResponseForbidden(
                '<div style="text-align:center;padding:4rem">'
                '<h2 style="font-size:1.25rem;font-weight:bold;color:#ef4444">Acceso Restringido</h2>'
                '<p style="opacity:0.6;margin-top:0.5rem">No tienes permisos para realizar esta acción.</p>'
                '<a href="/" style="margin-top:1rem;display:inline-block">Ir al Inicio</a>'
                '</div>'
            )
        return super().dispatch(request, *args, **kwargs)


class RoleRequiredMixin(AccessMixin):
    """
    Mixin that requires the user to have at least one of the specified roles.
    Usage:
        class MyView(RoleRequiredMixin, TemplateView):
            required_roles = {"DO", "LA"}
    """

    required_roles = set()

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not user_has_any_role(request.user, self.required_roles):
            return HttpResponseForbidden(
                '<div style="text-align:center;padding:4rem">'
                '<h2 style="font-size:1.25rem;font-weight:bold;color:#ef4444">Acceso Restringido</h2>'
                '<p style="opacity:0.6;margin-top:0.5rem">No tienes permisos para acceder a esta sección.</p>'
                '<a href="/" style="margin-top:1rem;display:inline-block">Ir al Inicio</a>'
                '</div>'
            )
        return super().dispatch(request, *args, **kwargs)


class FinancialAccessMixin(RoleFlagRequiredMixin):
    """Restricts access to financial views — configurable via can_access_financials flag on Role."""
    required_role_flag = "can_access_financials"


class PricingEditMixin(RoleRequiredMixin):
    """Restricts pricing edit access (DO role or staff)."""
    required_roles = PRICING_EDIT_ROLES


class ExecutiveAccessMixin(RoleRequiredMixin):
    """Restricts access to executive dashboards."""
    required_roles = EXECUTIVE_ROLES


class OperationalAccessMixin(RoleRequiredMixin):
    """Restricts access to operational views."""
    required_roles = OPERATIONAL_ROLES


def _user_has_role_flag(user, flag: str) -> bool:
    """Return True if the user has at least one role with the given boolean flag set."""
    if user.is_staff:
        return True
    try:
        return user.user_roles.filter(**{f"role__{flag}": True}).exists()
    except Exception:
        return False


def role_permissions(request):
    """
    Context processor that adds role-based permission flags to all templates.
    Add 'apps.common.mixins.role_permissions' to TEMPLATES context_processors.
    """
    user = request.user
    if not user.is_authenticated:
        return {
            "can_view_financials": False,
            "can_edit_pricing": False,
            "can_view_executive": False,
            "can_view_operations": False,
            "can_create_projects": False,
            "can_edit_projects": False,
            "can_manage_third_parties": False,
            "can_manage_allocations": False,
            "can_view_terceros": False,
            "can_view_services": False,
            "can_view_pricing": False,
            "can_view_organization": False,
            "can_view_portfolio": False,
            "can_view_capacity": False,
            "can_view_timetracking": False,
            "can_view_calendar": False,
            "can_import_data": False,
            "can_manage_teams": False,
        }
    return {
        "can_view_financials": _user_has_role_flag(user, "can_access_financials"),
        "can_edit_pricing": user_can_edit_pricing(user),
        "can_view_executive": user_can_view_executive(user),
        "can_view_operations": user_can_view_operations(user),
        "can_create_projects": _user_has_role_flag(user, "can_create_projects"),
        "can_edit_projects": _user_has_role_flag(user, "can_edit_projects"),
        "can_manage_third_parties": _user_has_role_flag(user, "can_manage_third_parties"),
        "can_manage_allocations": _user_has_role_flag(user, "can_manage_allocations"),
        "can_view_terceros": _user_has_role_flag(user, "can_view_terceros"),
        "can_view_services": _user_has_role_flag(user, "can_view_services"),
        "can_view_pricing": _user_has_role_flag(user, "can_view_pricing"),
        "can_view_organization": _user_has_role_flag(user, "can_view_organization"),
        "can_view_portfolio": _user_has_role_flag(user, "can_view_portfolio"),
        "can_view_capacity": _user_has_role_flag(user, "can_view_capacity"),
        "can_view_timetracking": _user_has_role_flag(user, "can_view_timetracking"),
        "can_view_calendar": _user_has_role_flag(user, "can_view_calendar"),
        "can_import_data": _user_has_role_flag(user, "can_import_data"),
        "can_manage_teams": _user_has_role_flag(user, "can_manage_teams"),
    }


# ---------------------------------------------------------------------------
# Audit
# ---------------------------------------------------------------------------

class AuditMixin:
    """
    Mixin that automatically creates AuditLog entries on save and delete.

    To track the user and IP address, set `_audit_user` and `_audit_ip`
    attributes on the model instance before calling save() or delete().
    """

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        action = AuditLog.Action.CREATE if is_new else AuditLog.Action.UPDATE

        # Capture changes for updates
        changes = {}
        if not is_new:
            try:
                old_instance = self.__class__.objects.get(pk=self.pk)
                for field in self._meta.fields:
                    old_value = getattr(old_instance, field.attname)
                    new_value = getattr(self, field.attname)
                    if old_value != new_value:
                        changes[field.name] = {
                            "old": str(old_value),
                            "new": str(new_value),
                        }
            except self.__class__.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        AuditLog.objects.create(
            user=getattr(self, "_audit_user", None),
            action=action,
            model_name=self.__class__.__name__,
            object_id=str(self.pk),
            changes=changes,
            ip_address=getattr(self, "_audit_ip", None),
        )

    def delete(self, *args, **kwargs):
        AuditLog.objects.create(
            user=getattr(self, "_audit_user", None),
            action=AuditLog.Action.DELETE,
            model_name=self.__class__.__name__,
            object_id=str(self.pk),
            changes={},
            ip_address=getattr(self, "_audit_ip", None),
        )
        return super().delete(*args, **kwargs)
