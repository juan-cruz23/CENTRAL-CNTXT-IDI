from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, TemplateView, View

from apps.accounts.models import Role, User, UserRole


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["user_roles"] = user.user_roles.select_related("role").all()
        return context


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class UserManagementView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    """Manage users and their role assignments."""

    model = User
    template_name = "accounts/user_management.html"
    context_object_name = "users"

    def get_queryset(self):
        return User.objects.filter(is_active=True).prefetch_related(
            "user_roles__role"
        ).order_by("first_name", "last_name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["all_roles"] = Role.objects.all().order_by("code")

        # Build user list with their roles
        user_list = []
        for user in context["users"]:
            current_roles = set(
                ur.role_id for ur in user.user_roles.all()
            )
            primary_role = next(
                (ur.role for ur in user.user_roles.all() if ur.is_primary),
                None,
            )
            user_list.append({
                "user": user,
                "roles": [ur.role for ur in user.user_roles.all()],
                "primary_role": primary_role,
                "current_role_ids": current_roles,
            })
        context["user_list"] = user_list
        return context


class UserRoleUpdateView(LoginRequiredMixin, StaffRequiredMixin, View):
    """HTMX endpoint: update roles for a user."""

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        selected_roles = request.POST.getlist("roles")
        primary_role_id = request.POST.get("primary_role")

        # Remove all current roles
        UserRole.objects.filter(user=user).delete()

        # Add selected roles
        for role_id in selected_roles:
            try:
                role = Role.objects.get(pk=role_id)
                UserRole.objects.create(
                    user=user,
                    role=role,
                    is_primary=(str(role.pk) == primary_role_id),
                )
            except Role.DoesNotExist:
                pass

        messages.success(
            request,
            f"Roles de {user.get_full_name()} actualizados.",
        )
        return redirect("accounts:user_management")
