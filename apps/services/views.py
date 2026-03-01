from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from apps.services.forms import ServiceTemplateForm
from apps.services.models import (
    ProjectCategory,
    ProjectPhase,
    ServiceTemplate,
)


class ProjectCategoryListView(LoginRequiredMixin, ListView):
    model = ProjectCategory
    template_name = "services/projectcategory_list.html"
    context_object_name = "categories"


class ProjectPhaseListView(LoginRequiredMixin, ListView):
    model = ProjectPhase
    template_name = "services/projectphase_list.html"
    context_object_name = "phases"


class ServiceTemplateListView(LoginRequiredMixin, ListView):
    model = ServiceTemplate
    template_name = "services/servicetemplate_list.html"
    context_object_name = "service_templates"


class ServiceTemplateDetailView(LoginRequiredMixin, DetailView):
    model = ServiceTemplate
    template_name = "services/servicetemplate_detail.html"
    context_object_name = "service_template"


class ServiceTemplateCreateView(LoginRequiredMixin, CreateView):
    model = ServiceTemplate
    form_class = ServiceTemplateForm
    template_name = "services/servicetemplate_form.html"
    success_url = reverse_lazy("services:servicetemplate_list")


class ServiceTemplateUpdateView(LoginRequiredMixin, UpdateView):
    model = ServiceTemplate
    form_class = ServiceTemplateForm
    template_name = "services/servicetemplate_form.html"
    success_url = reverse_lazy("services:servicetemplate_list")


class ServiceTemplateDeleteView(LoginRequiredMixin, DeleteView):
    model = ServiceTemplate
    template_name = "services/servicetemplate_confirm_delete.html"
    success_url = reverse_lazy("services:servicetemplate_list")
