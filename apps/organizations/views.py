from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

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
