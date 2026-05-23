from django import forms as django_forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView, UpdateView, View

from apps.accounts.models import AccessPackage, Role, User, UserRole, WorkSchedule


class ProfileForm(django_forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone", "avatar"]
        widgets = {
            "first_name": django_forms.TextInput(attrs={"class": "input input-bordered w-full"}),
            "last_name": django_forms.TextInput(attrs={"class": "input input-bordered w-full"}),
            "email": django_forms.EmailInput(attrs={"class": "input input-bordered w-full"}),
            "phone": django_forms.TextInput(attrs={"class": "input input-bordered w-full"}),
        }


class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = "accounts/profile.html"

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_roles"] = self.request.user.user_roles.select_related("role").all()
        return context

    def get_success_url(self):
        return reverse_lazy("accounts:profile")


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
    """Display & update roles for a user."""

    template_name = "accounts/user_role_form.html"

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        all_roles = Role.objects.filter(is_active=True).order_by("code")
        current_role_ids = set(
            UserRole.objects.filter(user=user).values_list("role_id", flat=True)
        )
        return TemplateResponse(
            request,
            self.template_name,
            {
                "target_user": user,
                "all_roles": all_roles,
                "current_role_ids": current_role_ids,
            },
        )

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        selected_role_ids = request.POST.getlist("roles")

        # Remove all current roles
        UserRole.objects.filter(user=user).delete()

        # Resolver y agregar roles preservando el orden de exhibición (code).
        # El primero marcado queda como principal.
        roles = list(
            Role.objects.filter(pk__in=selected_role_ids).order_by("code")
        )
        for idx, role in enumerate(roles):
            UserRole.objects.create(
                user=user,
                role=role,
                is_primary=(idx == 0),
            )

        messages.success(
            request,
            f"Roles de {user.get_full_name()} actualizados.",
        )
        return redirect("accounts:user_management")


# ---------------------------------------------------------------------------
# Role CRUD (Maestros)
# ---------------------------------------------------------------------------
class RoleForm(django_forms.ModelForm):
    class Meta:
        model = Role
        fields = ["code", "name", "description", "default_hourly_rate", "is_leader", "can_access_financials", "can_access_all_projects", "is_active"]
        widgets = {"description": django_forms.Textarea(attrs={"rows": 3, "class": "textarea textarea-bordered w-full"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, django_forms.CheckboxInput):
                widget.attrs["class"] = "checkbox"
            elif not isinstance(widget, django_forms.Textarea):
                widget.attrs["class"] = "input input-bordered w-full"


class RoleListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Role
    template_name = "accounts/role_list.html"
    context_object_name = "roles"

    def get_queryset(self):
        return Role.objects.prefetch_related("user_roles__user").order_by("code")


class RoleCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Role
    form_class = RoleForm
    template_name = "accounts/role_form.html"

    def get_success_url(self):
        return reverse_lazy("accounts:role_list")


class RoleUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Role
    form_class = RoleForm
    template_name = "accounts/role_form.html"

    def get_success_url(self):
        return reverse_lazy("accounts:role_list")


class RoleDeleteView(LoginRequiredMixin, StaffRequiredMixin, View):
    def post(self, request, pk):
        role = get_object_or_404(Role, pk=pk)
        role.delete()
        return HttpResponse(status=204, headers={"HX-Redirect": str(reverse_lazy("accounts:role_list"))})


# ---------------------------------------------------------------------------
# User creation
# ---------------------------------------------------------------------------
class UserCreateForm(django_forms.ModelForm):
    password1 = django_forms.CharField(
        label="Contraseña",
        widget=django_forms.PasswordInput(attrs={"class": "input input-bordered w-full"}),
    )
    password2 = django_forms.CharField(
        label="Confirmar contraseña",
        widget=django_forms.PasswordInput(attrs={"class": "input input-bordered w-full"}),
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "phone", "is_staff"]
        widgets = {
            "first_name": django_forms.TextInput(attrs={"class": "input input-bordered w-full"}),
            "last_name": django_forms.TextInput(attrs={"class": "input input-bordered w-full"}),
            "username": django_forms.TextInput(attrs={"class": "input input-bordered w-full"}),
            "email": django_forms.EmailInput(attrs={"class": "input input-bordered w-full"}),
            "phone": django_forms.TextInput(attrs={"class": "input input-bordered w-full"}),
            "is_staff": django_forms.CheckboxInput(attrs={"class": "checkbox"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Las contraseñas no coinciden.")
        return cleaned_data


class UserCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = User
    form_class = UserCreateForm
    template_name = "accounts/user_form.html"

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data["password1"])
        user.save()
        self._plain_password = form.cleaned_data["password1"]
        return redirect(reverse_lazy("accounts:user_created", kwargs={"pk": user.pk}) + f"?pwd={self._plain_password}")

    def get_success_url(self):
        return reverse_lazy("accounts:user_management")


class UserCreatedView(LoginRequiredMixin, StaffRequiredMixin, TemplateView):
    template_name = "accounts/user_created.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["new_user"] = get_object_or_404(User, pk=self.kwargs["pk"])
        context["plain_password"] = self.request.GET.get("pwd", "")
        return context


class UserUpdateForm(django_forms.ModelForm):
    new_password = django_forms.CharField(
        label="Nueva contraseña (dejar vacío para no cambiar)",
        required=False,
        widget=django_forms.PasswordInput(attrs={"class": "input input-bordered w-full", "autocomplete": "new-password"}),
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "phone", "is_staff", "is_active"]
        widgets = {
            "first_name": django_forms.TextInput(attrs={"class": "input input-bordered w-full"}),
            "last_name": django_forms.TextInput(attrs={"class": "input input-bordered w-full"}),
            "username": django_forms.TextInput(attrs={"class": "input input-bordered w-full"}),
            "email": django_forms.EmailInput(attrs={"class": "input input-bordered w-full"}),
            "phone": django_forms.TextInput(attrs={"class": "input input-bordered w-full"}),
            "is_staff": django_forms.CheckboxInput(attrs={"class": "checkbox"}),
            "is_active": django_forms.CheckboxInput(attrs={"class": "checkbox"}),
        }


class UserUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "accounts/user_update_form.html"

    def form_valid(self, form):
        user = form.save(commit=False)
        new_password = form.cleaned_data.get("new_password")
        if new_password:
            user.set_password(new_password)
        user.save()
        messages.success(self.request, f"Usuario {user.get_full_name()} actualizado.")
        return redirect(reverse_lazy("accounts:user_management"))

    def get_success_url(self):
        return reverse_lazy("accounts:user_management")


# ---------------------------------------------------------------------------
# AccessPackage CRUD (Maestros)
# ---------------------------------------------------------------------------
class AccessPackageForm(django_forms.ModelForm):
    class Meta:
        model = AccessPackage
        fields = ["code", "name", "description", "is_active"]
        widgets = {
            "code": django_forms.TextInput(attrs={"class": "input input-bordered w-full"}),
            "name": django_forms.TextInput(attrs={"class": "input input-bordered w-full"}),
            "description": django_forms.Textarea(attrs={"rows": 4, "class": "textarea textarea-bordered w-full"}),
            "is_active": django_forms.CheckboxInput(attrs={"class": "checkbox"}),
        }


class AccessPackageListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = AccessPackage
    template_name = "accounts/access_package_list.html"
    context_object_name = "packages"

    def get_queryset(self):
        return AccessPackage.objects.all()


class AccessPackageCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = AccessPackage
    form_class = AccessPackageForm
    template_name = "accounts/access_package_form.html"

    def get_success_url(self):
        return reverse_lazy("accounts:access_package_list")


class AccessPackageUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = AccessPackage
    form_class = AccessPackageForm
    template_name = "accounts/access_package_form.html"

    def get_success_url(self):
        return reverse_lazy("accounts:access_package_list")


class AccessPackageDeleteView(LoginRequiredMixin, StaffRequiredMixin, View):
    def post(self, request, pk):
        pkg = get_object_or_404(AccessPackage, pk=pk)
        if pkg.project_count > 0:
            return HttpResponse(
                f'<div class="alert alert-error text-sm">No se puede eliminar: {pkg.project_count} proyecto(s) usan este paquete.</div>',
                status=400,
            )
        pkg.delete()
        return HttpResponse(status=204, headers={"HX-Redirect": str(reverse_lazy("accounts:access_package_list"))})


# ---------------------------------------------------------------------------
# WorkSchedule CRUD (Maestros)
# ---------------------------------------------------------------------------
class WorkScheduleForm(django_forms.ModelForm):
    class Meta:
        model = WorkSchedule
        fields = ["name", "weekly_hours", "is_active"]
        widgets = {
            "name": django_forms.TextInput(attrs={"class": "input input-bordered w-full"}),
            "weekly_hours": django_forms.NumberInput(attrs={"class": "input input-bordered w-full", "step": "0.5", "min": "1"}),
        }


class WorkScheduleListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = WorkSchedule
    template_name = "accounts/work_schedule_list.html"
    context_object_name = "schedules"
    ordering = ["-weekly_hours"]


class WorkScheduleCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = WorkSchedule
    form_class = WorkScheduleForm
    template_name = "accounts/work_schedule_form.html"
    success_url = reverse_lazy("accounts:work_schedule_list")


class WorkScheduleUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = WorkSchedule
    form_class = WorkScheduleForm
    template_name = "accounts/work_schedule_form.html"
    success_url = reverse_lazy("accounts:work_schedule_list")


class WorkScheduleDeleteView(LoginRequiredMixin, StaffRequiredMixin, View):
    def post(self, request, pk):
        schedule = get_object_or_404(WorkSchedule, pk=pk)
        schedule.delete()
        return HttpResponse(status=204, headers={"HX-Redirect": str(reverse_lazy("accounts:work_schedule_list"))})
