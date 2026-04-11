from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from apps.organizations.forms import OperativeLineForm
from apps.organizations.models import BusinessUnit, OperativeLine, OrganizationalSystem


class OrganizationalSystemListView(LoginRequiredMixin, ListView):
    model = OrganizationalSystem
    template_name = "organizations/organizationalsystem_list.html"
    context_object_name = "systems"


class BusinessUnitListView(LoginRequiredMixin, ListView):
    model = BusinessUnit
    template_name = "organizations/businessunit_list.html"
    context_object_name = "business_units"


class OperativeLineListView(LoginRequiredMixin, ListView):
    model = OperativeLine
    template_name = "organizations/operativeline_list.html"
    context_object_name = "operative_lines"


class OperativeLineCreateView(LoginRequiredMixin, CreateView):
    model = OperativeLine
    form_class = OperativeLineForm
    template_name = "organizations/operativeline_form.html"
    success_url = reverse_lazy("organizations:operativeline_list")


class OperativeLineUpdateView(LoginRequiredMixin, UpdateView):
    model = OperativeLine
    form_class = OperativeLineForm
    template_name = "organizations/operativeline_form.html"
    success_url = reverse_lazy("organizations:operativeline_list")


class OperativeLineDeleteView(LoginRequiredMixin, DeleteView):
    model = OperativeLine
    template_name = "organizations/operativeline_confirm_delete.html"
    success_url = reverse_lazy("organizations:operativeline_list")
